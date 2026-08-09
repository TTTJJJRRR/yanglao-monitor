"""真实雷达数据源（M1 接入点）：相位信号 → 真实生命体征估计。

- 默认不连硬件：若未配置 RADAR_PORT / RADAR_BAUD，自动回退 SyntheticPhaseProvider。
- 真实路径：IWR6843AOP OOB TLV -> 提取检测点 -> 用点云序列构造 phase_window ->
  喂给 MmVitalEstimator，输出 breath_rate / heart_rate。
- 同时暴露 next_frame()（最近一帧点云）与 next_vital()（生命体征），供后续行为 CNN /
  生命体征界面复用。
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

from .mmvital_estimator import MmVitalEstimator, synthesize_chest_signal
from .oob_tlv import iter_frames
from .dual_vitals import estimate_dual
from ..models import VitalSource

try:
    import serial  # type: ignore
except ImportError:  # pragma: no cover - 边缘侧可选依赖
    serial = None


class PhaseProvider:
    def next_window(self) -> list[float] | None:
        raise NotImplementedError


class SyntheticPhaseProvider(PhaseProvider):
    """演示用合成相位源：生成频率已知、带轻微抖动的胸腔信号。"""

    def __init__(self, fs: float = 20.0, breath_hz: float = 0.25, heart_hz: float = 1.1, seed: int = 7):
        self.fs = fs
        self.breath_hz = breath_hz
        self.heart_hz = heart_hz
        self.seed = seed

    def next_window(self) -> list[float]:
        return synthesize_chest_signal(self.breath_hz, self.heart_hz, self.fs, 5.0, noise=0.05, seed=self.seed)


@dataclass
class _RadarConfig:
    port: str | None
    baud: int


class RadarPhaseProvider(PhaseProvider):
    """IWR6843AOP OOB TLV 真实雷达相位源。

    - 通过环境变量 RADAR_PORT / RADAR_BAUD 启用；
    - 解析失败或未配置时，外层 MmVitalSource 自动退回 SyntheticPhaseProvider；
    - next_frame() 返回最近一帧点云，next_window() 返回最近一段相位/距离序列。
    """

    def __init__(self, fs: float = 20.0, window_size: int = 100):
        self.fs = fs
        self.window_size = window_size
        self._cfg = _RadarConfig(
            port=os.getenv("RADAR_PORT"),
            baud=int(os.getenv("RADAR_BAUD", "921600")),
        )
        self._serial = None
        self._buffer = b""
        self._phase_samples: list[float] = []
        self._latest_points: Any = None
        self._enabled = bool(self._cfg.port) and serial is not None
        if self._enabled:
            try:
                self._serial = serial.Serial(self._cfg.port, self._cfg.baud, timeout=0.2)
            except Exception:
                self._serial = None
                self._enabled = False

    def _poll_frames(self) -> list[Any]:
        if not self._enabled or self._serial is None:
            return []
        try:
            chunk = self._serial.read(4096)
        except Exception:
            return []
        if chunk:
            self._buffer += chunk
        frames = iter_frames(self._buffer)
        if frames:
            last_points = frames[-1]
            self._latest_points = last_points
            self._phase_samples.extend(self._points_to_signal(last_points))
            self._buffer = b""
        return frames

    def _points_to_signal(self, points: Any) -> list[float]:
        if points is None:
            return []
        try:
            import numpy as np

            arr = np.asarray(points, dtype=np.float32)
            if arr.size == 0:
                return []
            if arr.ndim != 2 or arr.shape[1] < 3:
                return []
            return [float(np.linalg.norm(arr[:, :3], axis=1).mean())]
        except Exception:
            return []

    def next_frame(self):
        frames = self._poll_frames()
        if frames:
            return frames[-1]
        return None

    def next_window(self) -> list[float] | None:
        if not self._enabled:
            return None
        deadline = time.time() + 0.5
        while len(self._phase_samples) < self.window_size and time.time() < deadline:
            self._poll_frames()
            if len(self._phase_samples) < self.window_size and self._serial is not None:
                time.sleep(0.02)
        if len(self._phase_samples) < 8:
            return None
        if len(self._phase_samples) > self.window_size:
            return self._phase_samples[-self.window_size :]
        return list(self._phase_samples)

    def next_vital(self) -> dict | None:
        window = self.next_window()
        if window is None:
            return None
        est = MmVitalEstimator(self.fs).estimate(window)
        return {
            "timestamp_ms": int(time.time() * 1000),
            "device_id": "RADAR_01",
            "breath_rate": est.breath_rate,
            "heart_rate": est.heart_rate,
            "chest_displacement_mm": round(max(window) - min(window), 3) if window else None,
            "motion_flag": est.motion_flag,
            "ahi_index": None,
            "source": VitalSource.real.value,
        }


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
        if provider is not None:
            self.provider = provider
        else:
            radar_provider = RadarPhaseProvider(fs)
            self.provider = radar_provider if radar_provider._enabled else SyntheticPhaseProvider(fs)

    def next_vital(self) -> dict | None:
        """返回一帧双估计器投票后的真实生命体征;provider 无有效帧时返回 None。

        统一雷达 / 合成两种 provider:都取相位窗口 → estimate_dual 投票。
        投票结果带 vital_agreement / needs_review / watch_reason,供融合层与家属端
        区分"高可信体征"与"需盯防" —— 关键体征永不被静默当成安全。
        """
        window = self.provider.next_window()
        if window is None:
            return None
        dual = estimate_dual(window, self.fs)
        return {
            "timestamp_ms": int(time.time() * 1000),
            "device_id": self.device_id,
            "breath_rate": dual.breath_rate,
            "heart_rate": dual.heart_rate,
            "chest_displacement_mm": round(max(window) - min(window), 3) if window else None,
            "motion_flag": dual.motion_flag,
            "quality": dual.quality,
            "vital_agreement": dual.agreement,
            "needs_review": dual.needs_review,
            "watch_reason": dual.watch_reason,
            "ahi_index": None,
            "source": VitalSource.real.value,
        }
