"""EEMD 生命体征估计（融合 phish-tech 开源思路的「第二个估计器」）。

背景：GitHub 前沿检索发现 `phish-tech/mmWave-Heartbeat-Dataset-Preprocessing-Toolbox-`
用 **EEMD（集合经验模态分解）** 从雷达相位信号分离呼吸/心跳。本项目已有一个
纯 Python 的 DFT 周期图估计器（`mmvital_estimator.py`）。本模块把 EEMD 也用纯
Python 实现（不依赖 numpy/MATLAB），作为**独立第二估计器**，与 DFT 互相交叉验证——
两个方法在同一信号上一致，才说明生命体征估计可信，而非某单一算法的巧合。

- EemdVitalsEstimator.estimate(phase_signal, fs)：返回与 DFT 同构的 VitalEstimate。
- 复用 `mmvital_estimator._periodogram_peak` 求各 IMF 主频，保持单一频谱口径。
- EMD 用线性包络（对频带良好分离的正弦足够）；EEMD 加噪集合平均抑制模态混叠。

⚠️ 诚实边界：
1. 本实现是 faithful 的纯 Python 复刻，非 MATLAB 原版；用于交叉验证与无依赖环境。
2. 沙箱离线 + 原仓库为 MATLAB，无法拉取真实 .bin；真实数据验证见 `load_phish_bin`
   （扩展点，需按其 MATLAB loader 对齐字节格式后接入）。
3. 合成信号明确标注为合成输入；跑的是真实算法，不是假生命体征。
"""
from __future__ import annotations

import bisect
import math
import random
import struct
from dataclasses import dataclass

from .mmvital_estimator import VitalEstimate, _periodogram_peak, _detrend


# --------------------------------------------------------------------------
# EMD / EEMD 纯 Python 实现（线性包络，无 numpy）
# --------------------------------------------------------------------------

def _extrema(sig: list[float]) -> tuple[list[tuple[int, float]], list[tuple[int, float]]]:
    """找局部极大/极小点，并把首尾样本补进包络以保证端点定义。"""
    n = len(sig)
    maxs: list[tuple[int, float]] = []
    mins: list[tuple[int, float]] = []
    for i in range(1, n - 1):
        if sig[i] > sig[i - 1] and sig[i] >= sig[i + 1]:
            maxs.append((i, sig[i]))
        elif sig[i] < sig[i - 1] and sig[i] <= sig[i + 1]:
            mins.append((i, sig[i]))
    maxs.insert(0, (0, sig[0]))
    maxs.append((n - 1, sig[n - 1]))
    mins.insert(0, (0, sig[0]))
    mins.append((n - 1, sig[n - 1]))
    return maxs, mins


def _linear_interp(xs: list[int], ys: list[float], xq: list[int]) -> list[float]:
    """对查询点 xq 在 (xs, ys) 上做线性插值（xs 升序）。"""
    out: list[float] = []
    for x in xq:
        if x <= xs[0]:
            out.append(ys[0])
        elif x >= xs[-1]:
            out.append(ys[-1])
        else:
            j = bisect.bisect_right(xs, x)
            x0, x1 = xs[j - 1], xs[j]
            y0, y1 = ys[j - 1], ys[j]
            t = (x - x0) / (x1 - x0) if x1 > x0 else 0.0
            out.append(y0 + t * (y1 - y0))
    return out


def _emd(sig: list[float], max_imf: int = 8, max_sift: int = 15, tol: float = 0.1) -> list[list[float]]:
    """单次 EMD：把信号筛分成若干 IMF（高频在前）。"""
    n = len(sig)
    xs = list(range(n))
    residue = list(sig)
    imfs: list[list[float]] = []
    sig_power = sum(x * x for x in sig) + 1e-12
    for _ in range(max_imf):
        h = list(residue)
        for _ in range(max_sift):
            maxs, mins = _extrema(h)
            up = _linear_interp([i for i, _ in maxs], [v for _, v in maxs], xs)
            lo = _linear_interp([i for i, _ in mins], [v for _, v in mins], xs)
            mean = [(u + l) / 2.0 for u, l in zip(up, lo)]
            h_new = [h[i] - mean[i] for i in range(n)]
            num = sum((h[i] - h_new[i]) ** 2 for i in range(n))
            den = sum(h[i] * h[i] for i in range(n)) + 1e-12
            sd = num / den
            h = h_new
            if sd < tol:
                break
        imfs.append(h)
        residue = [residue[i] - h[i] for i in range(n)]
        if sum(r * r for r in residue) < 1e-4 * sig_power:
            break
    return imfs


def eemd(
    sig: list[float],
    n_ensemble: int = 8,
    noise_ratio: float = 0.2,
    max_imf: int = 8,
    max_sift: int = 15,
    tol: float = 0.1,
    seed: int = 0,
) -> list[list[float]]:
    """EEMD：对多次加噪后的 EMD 结果做集合平均，抑制模态混叠。"""
    n = len(sig)
    rnd = random.Random(seed)
    sig_std = math.sqrt(sum(x * x for x in sig) / n) + 1e-9
    noise_std = noise_ratio * sig_std
    acc: list[list[float]] | None = None
    for _ in range(n_ensemble):
        noise = [rnd.gauss(0.0, noise_std) for _ in range(n)]
        imfs = _emd([sig[i] + noise[i] for i in range(n)], max_imf, max_sift, tol)
        if acc is None:
            acc = [[0.0] * n for _ in imfs]
        for j, imf in enumerate(imfs):
            for i in range(n):
                acc[j][i] += imf[i]
    if acc is None:
        return []
    k = n_ensemble
    return [[v / k for v in imf] for imf in acc]


# --------------------------------------------------------------------------
# 估计器接口（与 MmVitalEstimator 同构）
# --------------------------------------------------------------------------

def estimate_eemd(phase_signal: list[float], fs: float) -> VitalEstimate:
    """用 EEMD 分解各 IMF，按频带挑呼吸/心跳分量（与 DFT 同口径交叉验证）。"""
    if not phase_signal or len(phase_signal) < 8:
        return VitalEstimate(None, None, True, 0.0)
    sig = _detrend(phase_signal)
    imfs = eemd(sig, n_ensemble=8, noise_ratio=0.2)
    if not imfs:
        return VitalEstimate(None, None, True, 0.0)
    breath_f, breath_mag = 0.0, 0.0
    heart_f, heart_mag = 0.0, 0.0
    for imf in imfs:
        f, mag = _periodogram_peak(imf, fs, 0.05, 3.0)
        if 0.1 <= f <= 0.5 and mag > breath_mag:
            breath_f, breath_mag = f, mag
        if 0.8 <= f <= 2.0 and mag > heart_mag:
            heart_f, heart_mag = f, mag
    breath_rate = round(breath_f * 60.0, 1) if breath_f > 0 else None
    heart_rate = round(heart_f * 60.0, 1) if heart_f > 0 else None
    motion_flag = breath_mag < 1e-6
    total = sum(x * x for x in sig) + 1e-12
    quality = min(1.0, (breath_mag + heart_mag) / math.sqrt(total) / math.sqrt(len(sig)))
    return VitalEstimate(breath_rate, heart_rate, motion_flag, round(quality, 3))


class EemdVitalsEstimator:
    """封装 EEMD 估计器；可与 MmVitalEstimator 双估计器投票/交叉验证。"""

    def __init__(self, fs: float = 20.0):
        self.fs = fs

    def estimate(self, phase_signal: list[float]) -> VitalEstimate:
        return estimate_eemd(phase_signal, self.fs)


def load_phish_bin(path: str, fs: float = 20.0) -> list[float]:
    """读取 phish-tech 开源 77GHz 原始 .bin 的扩展点（真实数据验证用）。

    ⚠️ 该仓库用 MATLAB 解析（range-FFT → 相位）；确切字节格式需按其 loader
    对齐。本函数先抛 NotImplemented 以明确「此处需接真实解析」，避免假装能读。
    沙箱离线也无法拉取真实文件——请在本机取得 .bin 后，按其 MATLAB 步骤导出
    相位序列（list[float]），再传给 `estimate_eemd` / `estimate_vitals` 即可。
    """
    _ = path, fs  # 占位，避免未用参数告警
    raise NotImplementedError(
        "load_phish_bin 需按 phish-tech 的 MATLAB loader 对齐字节格式后实现；"
        "请先取得真实 .bin，用其 MATLAB 流程导出相位序列(list[float])，"
        "再调用 estimate_eemd(phase) / estimate_vitals(phase) 完成真实验证。"
    )
