"""雷达行为分类模型接口（M2/M3 接缝 / 空挡接口）。

这是「真实雷达行为模型」接入系统的唯一契约。M1 硬件(IWR6843AOP)采集的数据
或专用跌倒数据集训练出的 CNN 将在未来实现本接口并 ``register_classifier`` 注册，
即可被 ``routers/edge.py`` 的 ``/api/edge/radar-frame`` 端点直接调用。

为什么需要它：
- 之前 ``/api/edge/behavior`` 直接接收外部 POST 的 action（演示时手敲假信号），
  无法区分「真模型输出」与「伪造」。本接口把「雷达信号 → 行为」这一步收敛到
  一个有类型的模型里，假数据无处藏身。
- 当前 ``StubBehaviorClassifier`` **显式拒绝伪造**：调用即抛 ``ModelNotLoadedError``，
  绝不返回随机/占位行为，防止被误当成品。

输入契约（真实模型就位后填充）：
- ``RadarFrame.signature`` = 一帧雷达信号张量。M1 形态为 TI IWR6843AOP 点云随时间的
  微多普勒图(micro-Doppler)；MMFi 来源为 mmwave 点云序列 → 微多普勒。
  形状/归一化由实现方与 docs §6 数据契约对齐。
- 输出 ``BehaviorPrediction.action`` 必须属于 ``BehaviorAction``
  (walking/sitting/lying/crouching/falling/still)。

接入示例（模型就绪后）：
    from app.inference.behavior_classifier import (
        BehaviorClassifier, BehaviorPrediction, RadarFrame, register_classifier,
    )
    class MmWaveCNN(BehaviorClassifier):
        def classify(self, frame: RadarFrame) -> BehaviorPrediction:
            # 真实推理：frame.signature → 6 类 softmax → 取 argmax
            action, conf = self._infer(frame.signature)
            return BehaviorPrediction(action=action, confidence=float(conf))
    register_classifier(MmWaveCNN())
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ..models import BehaviorAction


@dataclass
class RadarFrame:
    """模型输入契约：一帧雷达信号。

    ``signature`` 在真实模型就位前为 None；实现方负责把原始点云/微多普勒
    转成模型期望的张量。
    """

    device_id: str
    timestamp_ms: int
    signature: Any = None


@dataclass
class BehaviorPrediction:
    """模型输出契约。"""

    action: BehaviorAction
    confidence: float


class BehaviorClassifier(ABC):
    """雷达行为分类器接口。未来 CNN 实现此接口。"""

    @abstractmethod
    def classify(self, frame: RadarFrame) -> BehaviorPrediction:
        """输入雷达帧，输出行为 + 置信度。禁止返回伪造/随机结果。"""
        raise NotImplementedError


class ModelNotLoadedError(RuntimeError):
    """真实模型尚未接入时的显式错误（不是假检测）。"""


class StubBehaviorClassifier(BehaviorClassifier):
    """占位实现：明确拒绝伪造，调用即抛 ``ModelNotLoadedError``。

    真实模型（M1 数据 / 跌倒数据集训练）就位后，用 ``register_classifier``
    替换为具体实现即可，无需改动调用方。
    """

    def classify(self, frame: RadarFrame) -> BehaviorPrediction:
        raise ModelNotLoadedError(
            "雷达行为模型尚未接入（M1 硬件数据或专用跌倒数据集训练后填入）。"
            " 当前为显式空挡接口，不返回伪造行为。"
        )


_CLASSIFIER: BehaviorClassifier | None = None


def register_classifier(classifier: BehaviorClassifier) -> None:
    """注册真实模型实现（系统启动时或模型加载后调用一次）。"""
    global _CLASSIFIER
    _CLASSIFIER = classifier


def get_classifier() -> BehaviorClassifier:
    """获取当前分类器；未注册时返回显式 Stub（拒绝伪造）。"""
    return _CLASSIFIER or StubBehaviorClassifier()
