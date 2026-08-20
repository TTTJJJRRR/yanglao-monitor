"""多类雷达行为数据集加载器（M5：真实数据接入前的训练前置门禁）。

目录约定：data/radar/E<环境>/S<受试者>/A<class>/mmwave/frame*.bin
其中 A01-A08 映射到锁定的 8 类生产动作集。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

from .preprocess import load_mmwave_frames
from ...models import BehaviorAction


A_TO_BEHAVIOR = {
    "A01": BehaviorAction.walking,
    "A02": BehaviorAction.standing,
    "A03": BehaviorAction.sitting_still,
    "A04": BehaviorAction.standing_up,
    "A05": BehaviorAction.crouching,
    "A06": BehaviorAction.lying,
    "A07": BehaviorAction.lying_floor,
    "A08": BehaviorAction.falling,
}

LABEL_TO_INDEX = {
    BehaviorAction.walking: 0,
    BehaviorAction.standing: 1,
    BehaviorAction.sitting_still: 2,
    BehaviorAction.standing_up: 3,
    BehaviorAction.crouching: 4,
    BehaviorAction.lying: 5,
    BehaviorAction.lying_floor: 6,
    BehaviorAction.falling: 7,
    BehaviorAction.normal_activity: 0,
}

BEHAVIOR_TO_INDEX = {action: idx for idx, action in enumerate(A_TO_BEHAVIOR.values())}


@dataclass(frozen=True)
class RadarSample:
    frames: list[np.ndarray]
    label: BehaviorAction
    subject_id: str
    action_id: str
    path: Path


class RadarDataset:
    """扫描真实雷达目录树，按 A 编号自动标注。"""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.samples: list[RadarSample] = []
        self._load()

    def _candidate_dirs(self) -> Iterable[Path]:
        if not self.root.exists():
            return []
        candidates = [self.root]
        candidates.extend(self.root.glob("E*/S*/A*/mmwave"))
        candidates.extend(self.root.glob("A*/mmwave"))
        candidates.extend(self.root.glob("mmwave"))
        seen: set[Path] = set()
        for path in candidates:
            if path in seen or not path.exists():
                continue
            seen.add(path)
            yield path

    def _load(self) -> None:
        for mmwave_dir in self._candidate_dirs():
            if mmwave_dir.name != "mmwave":
                continue
            action_id = mmwave_dir.parent.name if mmwave_dir.parent else ""
            label = A_TO_BEHAVIOR.get(action_id)
            if label is None:
                # 支持 root 直接指向某个 Axx/mmwave 目录
                ancestor = mmwave_dir.parents[2] if len(mmwave_dir.parents) >= 3 else None
                if ancestor is not None and ancestor.name in A_TO_BEHAVIOR:
                    action_id = ancestor.name
                    label = A_TO_BEHAVIOR[action_id]
            if label is None:
                continue
            frames = load_mmwave_frames(str(mmwave_dir))
            if not frames:
                continue
            self.samples.append(
                RadarSample(
                    frames=frames,
                    label=label,
                    subject_id=mmwave_dir.parent.parent.name if mmwave_dir.parent and mmwave_dir.parent.parent else "unknown",
                    action_id=action_id,
                    path=mmwave_dir,
                )
            )

    def __len__(self) -> int:
        return len(self.samples)

    def __iter__(self):
        return iter(self.samples)

    @property
    def class_count(self) -> int:
        return len({sample.label for sample in self.samples})

    @property
    def min_frames_per_class(self) -> int:
        counts: dict[BehaviorAction, int] = {}
        for sample in self.samples:
            counts[sample.label] = counts.get(sample.label, 0) + len(sample.frames)
        return min(counts.values()) if counts else 0

    def to_training_pairs(self) -> list[tuple[list[np.ndarray], int]]:
        return [(sample.frames, LABEL_TO_INDEX[sample.label]) for sample in self.samples]
