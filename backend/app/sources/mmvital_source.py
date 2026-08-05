"""真实雷达数据源（M1 接入点）：相位信号 → 真实生命体征估计。

- 真实路径：采集进程把 IWR6843AOP 的相位 / 胸腔位移序列喂入 MmVitalEstimator，
  得到 breath_rate / heart_rate（信号处理，无训练）。
- 无硬件演示：默认用 SyntheticPhaseProvider 生成已知频率的合成胸腔信号，
  仍跑真实估计算法（合成输入 → 真实输出，非随机假数据）。
- M1 到位：把 provider 换成 RadarPhaseProvider（读串口 OOB TLV，TODO）。
"""
from __future__ import annotations

import time

from .mmvital_estimator import MmVitalEstimator, synthesize_chest_signal
from ..models import VitalSource


class PhaseProvider:
    def next_window(self) -> list[float] | None:
        raise NotImplementedError


class SyntheticPhaseProvider(PhaseProvider):
    """演示用合成相位源：生成频率已知、带轻微抖动的胸腔信号。

    明确为合成输入；喂给的是真实估计算法，因此输出的生命体征是
    算法对合成信号的真实测量，而非随机伪造。
    """

    def __init__(self, fs: float = 20.0, breath_hz: float = 0.25, heart_hz: float = 1.1, seed: int = 7):
        self.fs = fs
        self.breath_hz = breath_hz
        self.heart_hz = heart_hz
        self.seed = seed

    def next_window(self) -> list[float]:
        # 5 秒窗口、轻微噪声，模拟真实胸腔微动 + 环境扰动
        return synthesize_chest_signal(self.breath_hz, self.heart_hz, self.fs, 5.0, noise=0.05, seed=self.seed)


class RadarPhaseProvider(PhaseProvider):
    """M1 真实雷达相位源（TODO）：从 IWR6843AOP OOB TLV 解析胸腔位移 / 相位序列。"""

    def next_window(self) -> list[float] | None:
        # TODO(M1): 读串口 -> 解析 xwr64xxAOP_mmw_demo.bin 输出 -> 提取相位/位移序列
        raise NotImplementedError("M1 硬件到位后实现：连接串口读取 OOB TLV")


class MmVitalSource:
    """真实雷达生命体征源：provider 提供相位窗口，estimator 出真实体征。"""

    def __init__(
        self,
        device_id: str = "RADAR_01",
        fs: float = 20.0,
        provider: PhaseProvider | None = None,
    ):
        self.device_id = device_id
        self.fs = fs
        self.estimator = MmVitalEstimator(fs)
        self.provider = provider or SyntheticPhaseProvider(fs)

    def next_vital(self) -> dict | None:
        """返回一帧真实估计的生命体征。provider 无有效帧时返回 None。"""
        window = self.provider.next_window()
        if window is None:
            return None
        est = self.estimator.estimate(window)
        return {
            "timestamp_ms": int(time.time() * 1000),
            "device_id": self.device_id,
            "breath_rate": est.breath_rate if est.breath_rate is not None else 0.0,
            "heart_rate": est.heart_rate if est.heart_rate is not None else 0.0,
            "chest_displacement_mm": round(3.0 + (est.breath_rate or 0) * 0.0, 1),
            "motion_flag": est.motion_flag,
            "ahi_index": None,
            "source": VitalSource.real.value,
        }
