"""数据源切换模块（M0 收尾 + MMFi 验证包接入）。

- mock：复用 mock.py 生成器（由 main.mock_stream 写库 + 广播）。
- mmfi：读取 data/mmfi-sample/radar_sample.jsonl，仅广播不落库。
  原因：MMFi 样例的生命体征（breath_rate/heart_rate/ahi_index）为 null，
  不满足 VitalRecord 的非空约束，且样例本身只含雷达帧、无行为/报警真值，
  故只把帧结构映射到项目平坦 vital 契约并推送给前端做管道验证。
- real：真实雷达源（M0 占位 / M1 接 mmVital）。返回有效帧，写库 + 广播。
"""
import json
import threading
from pathlib import Path

from .sources.mmvital_source import MmVitalSource

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "mmfi-sample" / "radar_sample.jsonl"

AVAILABLE = ["mock", "mmfi", "real"]
_real = MmVitalSource()

_current_source = {"value": "mock"}
_lock = threading.Lock()


class MMFiSource:
    """读取 MMFi 验证包，循环提供与项目平坦 vital 契约兼容的帧。"""

    def __init__(self, path: Path = DATA_FILE):
        self.frames: list[dict] = []
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        self.frames.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        self._idx = 0

    def next_vital(self) -> dict | None:
        if not self.frames:
            return None
        raw = self.frames[self._idx % len(self.frames)]
        self._idx += 1
        return {
            "timestamp_ms": raw.get("timestamp_ms"),
            "device_id": raw.get("device_id", "MMFI_RADAR_SAMPLE"),
            "breath_rate": raw.get("breath_rate"),  # 可能为 None（样例无生命体征真值）
            "heart_rate": raw.get("heart_rate"),    # 可能为 None
            "chest_displacement_mm": raw.get("chest_displacement_mm"),
            "motion_flag": bool(raw.get("motion_flag", False)),
            "ahi_index": raw.get("ahi_index"),      # 可能为 None
            "source": "mmfi",
        }


_mmfi = MMFiSource()


def get_source() -> str:
    return _current_source["value"]


def set_source(value: str) -> bool:
    if value not in AVAILABLE:
        return False
    with _lock:
        _current_source["value"] = value
    return True


def available_sources() -> list[str]:
    return list(AVAILABLE)


def next_mmfi_messages() -> list[dict]:
    """构造 mmfi 模式下要广播的消息列表（仅 vital，不落库）。"""
    vital = _mmfi.next_vital()
    if vital is None:
        return []
    return [{"type": "vital", "data": vital}]


def next_real_vital() -> dict | None:
    """返回真实雷达源的一帧生命体征（M0 占位，M1 接 mmVital）。"""
    return _real.next_vital()
