"""回放数据源（A1）：把同学采集的 jsonl（已算好体征 + 动作标签）回放进后端。

⚠️ 诚实标注：这是「回放/演示」数据，NOT 实时检测。jsonl 里是**成品体征**
（breath_rate / heart_rate / motion_flag），**非 IWR6843AOP 原始雷达帧**；
仅用于验证前端管道与动作标签流转，**不写入数据库**（不污染真实记录）。

数据目录：`data/replay/**/*.jsonl`
- 动作标签从**文件名**识别：含 `sitting` → sitting_still，含 `walking` → walking。
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from ..models import BehaviorAction

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "replay"
STEP = 5  # 每次 next_messages() 推进的记录数（提速演示，原数据约 1 条/0.09s）


def _action_from_filename(name: str) -> str:
    """从 jsonl 文件名识别动作，落到 8 类安全集 BehaviorAction 值。"""
    n = name.lower()
    if "sitting" in n:
        return "sitting_still"
    if "walking" in n:
        return "walking"
    for v in {e.value for e in BehaviorAction}:
        if v in n:
            return v
    return "normal_activity"


class ReplaySource:
    """按时间顺序循环回放 data/replay 下各段，产出平坦 vital + behavior 消息。"""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.segments = self._load(data_dir)
        self._seg_idx = 0
        self._rec_idx = 0

    # ---- 加载 ----
    def _load(self, data_dir: Path) -> list[dict]:
        segments: list[dict] = []
        if not data_dir.exists():
            return segments
        for jsonl in sorted(data_dir.rglob("*.jsonl")):
            records: list[dict] = []
            try:
                for line in jsonl.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            except OSError:
                continue
            if records:
                segments.append({
                    "action": _action_from_filename(jsonl.name),
                    "start_ms": records[0].get("timestamp_ms") or 0,
                    "records": records,
                })
        segments.sort(key=lambda s: s["start_ms"])
        return segments

    # ---- 读取 ----
    @property
    def total_segments(self) -> int:
        return len(self.segments)

    def _next_record(self) -> tuple[dict | None, str | None]:
        """返回下一条原始记录 + 所属动作；到末尾自动循环。"""
        if not self.segments:
            return None, None
        seg = self.segments[self._seg_idx % len(self.segments)]
        if self._rec_idx >= len(seg["records"]):
            self._rec_idx = 0
            self._seg_idx += 1
            seg = self.segments[self._seg_idx % len(self.segments)]
        raw = seg["records"][self._rec_idx]
        self._rec_idx += 1
        return raw, seg["action"]

    def next_vital(self) -> dict | None:
        raw, _ = self._next_record()
        if raw is None:
            return None
        return self._flat_vital(raw)

    def next_messages(self) -> list[dict]:
        """推进 STEP 条记录，返回待广播消息（vital ×N + behavior ×1）。"""
        if not self.segments:
            return []
        out: list[dict] = []
        for _ in range(STEP):
            raw, _ = self._next_record()
            if raw is None:
                break
            out.append({"type": "vital", "data": self._flat_vital(raw)})
        seg = self.segments[self._seg_idx % len(self.segments)]
        out.append({"type": "behavior", "data": self._flat_behavior(seg["action"])})
        return out

    @staticmethod
    def _flat_vital(raw: dict) -> dict:
        """记录 -> 项目平坦 vital 契约。时间重打为 now（回放），原始 ts 仅作日志。"""
        return {
            "timestamp_ms": int(time.time() * 1000),
            "device_id": raw.get("device_id") or "REPLAY_01",
            "breath_rate": raw.get("breath_rate"),
            "heart_rate": raw.get("heart_rate"),
            "chest_displacement_mm": raw.get("chest_displacement_mm"),
            "motion_flag": bool(raw.get("motion_flag", False)),
            "ahi_index": raw.get("ahi_index"),
            "source": "replay",
        }

    @staticmethod
    def _flat_behavior(action: str) -> dict:
        return {
            "timestamp_ms": int(time.time() * 1000),
            "action": action,
            "emotion": "calm",
            "confidence": 0.85,  # 演示置信度，非真实模型输出
            "source": "replay",
        }
