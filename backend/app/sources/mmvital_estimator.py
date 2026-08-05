"""真实生命体征估计（mmVital 信号处理，纯 Python 实现，无训练）。

对应 M1 接入点：解析 TI IWR6843AOP 的相位 / 胸腔位移信号，
用带通 + 周期图(DFT 幅值)估计呼吸率与心率。这是信号处理
（与 mmVital-Signs 同原理），不依赖任何训练模型。

- estimate_vitals(phase_signal, fs)：对一段胸腔位移/相位序列估计
  breath_rate(0.1~0.5 Hz)、heart_rate(0.8~2.0 Hz)、motion_flag、quality。
- synthesize_chest_signal(...)：生成已知频率的合成胸腔信号，用于测试 / 无硬件演示
  （明确标注为合成输入，跑的是真实估计算法，不是随机假数据）。

边缘侧若安装 mmvital_signs，可直接调用其 vital_signs_estimator 替换本实现；
本模块保证无第三方包也能跑真实算法并测试。
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class VitalEstimate:
    breath_rate: float | None
    heart_rate: float | None
    motion_flag: bool
    quality: float  # 0~1 频谱纯度（越高越可信）


def _detrend(sig: list[float]) -> list[float]:
    n = len(sig)
    mean = sum(sig) / n
    return [x - mean for x in sig]


def _periodogram_peak(sig: list[float], fs: float, f_lo: float, f_hi: float) -> tuple[float, float]:
    """在 [f_lo, f_hi] 频带内用周期图(DFT 幅值)找主频与对应幅值。

    纯 Python DFT，仅对带内若干频率点采样，复杂度 O(N·Band)，
    对几十秒的窗口完全够用，且不依赖 numpy。
    """
    n = len(sig)
    best_f = 0.0
    best_mag = 0.0
    f = f_lo
    step = 0.025  # 0.025 Hz 频率分辨率，足够区分呼吸/心率
    while f <= f_hi:
        re = 0.0
        im = 0.0
        for k in range(n):
            ang = -2.0 * math.pi * f * (k / fs)
            re += sig[k] * math.cos(ang)
            im += sig[k] * math.sin(ang)
        mag = math.sqrt(re * re + im * im)
        if mag > best_mag:
            best_mag = mag
            best_f = f
        f += step
    return best_f, best_mag


def estimate_vitals(phase_signal: list[float], fs: float) -> VitalEstimate:
    """从胸腔位移/相位序列估计生命体征（信号处理，无训练）。"""
    if not phase_signal or len(phase_signal) < 8:
        return VitalEstimate(None, None, True, 0.0)
    sig = _detrend(phase_signal)
    # 呼吸带 0.1~0.5 Hz -> 6~30 次/分
    breath_f, breath_mag = _periodogram_peak(sig, fs, 0.1, 0.5)
    # 心带 0.8~2.0 Hz -> 48~120 bpm
    heart_f, heart_mag = _periodogram_peak(sig, fs, 0.8, 2.0)
    breath_rate = round(breath_f * 60.0, 1) if breath_f > 0 else None
    heart_rate = round(heart_f * 60.0, 1) if heart_f > 0 else None
    motion_flag = breath_mag < 1e-6  # 信号过弱视为遮挡 / 运动
    total = sum(x * x for x in sig) + 1e-12
    quality = min(1.0, (breath_mag + heart_mag) / math.sqrt(total) / math.sqrt(len(sig)))
    return VitalEstimate(breath_rate, heart_rate, motion_flag, round(quality, 3))


def synthesize_chest_signal(
    breath_hz: float,
    heart_hz: float,
    fs: float,
    duration_s: float,
    noise: float = 0.0,
    breath_amp: float = 1.0,
    heart_amp: float = 0.3,
    seed: int | None = None,
) -> list[float]:
    """生成合成胸腔位移信号（演示 / 测试用，明确为合成输入）。

    由两个正弦（呼吸 + 心跳）叠加噪声构成，作为真实估计器的输入。
    注意：这是「合成输入 → 真实算法输出」，不是假生命体征。
    """
    if seed is not None:
        random.seed(seed)
    n = int(fs * duration_s)
    out: list[float] = []
    for k in range(n):
        t = k / fs
        v = breath_amp * math.sin(2 * math.pi * breath_hz * t) + heart_amp * math.sin(2 * math.pi * heart_hz * t)
        if noise:
            v += random.uniform(-noise, noise)
        out.append(v)
    return out


class MmVitalEstimator:
    """封装真实估计器；边缘侧可替换为 mmvital_signs 的调用。"""

    def __init__(self, fs: float = 20.0):
        self.fs = fs

    def estimate(self, phase_signal: list[float]) -> VitalEstimate:
        return estimate_vitals(phase_signal, self.fs)
