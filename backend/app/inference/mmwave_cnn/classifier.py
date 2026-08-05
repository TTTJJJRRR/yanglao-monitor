"""MmWaveBehaviorCNN：实现 BehaviorClassifier，把真实 mmWave CNN 接进系统。

推理时 frame.signature 应为：
  - mmwave 目录路径（含 frame*.bin），或
  - 点云序列 list[np.ndarray (N,3)]
输出 BehaviorPrediction(action: BehaviorAction, confidence)。

torch 采用惰性导入：未注册本模型时，后端无需安装 torch。
"""
from __future__ import annotations

import os

from ..behavior_classifier import BehaviorClassifier, BehaviorPrediction, RadarFrame
from ...models import BehaviorAction
from .preprocess import load_mmwave_frames, preprocess_sequence

DEFAULT_WEIGHTS = os.path.join(os.path.dirname(__file__), "weights.pt")

# MMFi 官方动作顺序 A01..A27（索引 0..26 对应此序）
MMFI_ACTIONS = [
    "A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09",
    "A10", "A11", "A12", "A13", "A14", "A15", "A16", "A17", "A18", "A19",
    "A20", "A21", "A22", "A23", "A24", "A25", "A26", "A27",
]
# MMFi 动作 -> 本项目 BehaviorAction 的部分映射（项目不止跌倒，仅映射相关子集）
# falling 不在 MMFi 中，需 M1 硬件/专用跌倒集补充。
MMFI_TO_BEHAVIOR = {
    "A06": BehaviorAction.walking,         # 原地踏步 -> walking
    "A12": BehaviorAction.sitting_still,   # 低动作样本先映射为静态类
    "A19": BehaviorAction.sitting_still,   # 拾物 -> 静态/低速动作
    "A27": BehaviorAction.normal_activity, # 鞠躬 -> normal_activity
}


class MmWaveBehaviorCNN(BehaviorClassifier):
    def __init__(self, weights_path: str = DEFAULT_WEIGHTS, num_classes: int = 27, device: str = "cpu"):
        # 惰性导入 torch，避免后端常驻依赖
        import torch
        from .model import MmWaveCNN

        self._torch = torch
        self.device = device
        self.model = MmWaveCNN(num_classes)
        if os.path.exists(weights_path):
            self.model.load_state_dict(torch.load(weights_path, map_location=device))
        else:
            raise FileNotFoundError(f"权重未找到: {weights_path}，请先训练（见 train.py / Cursor 委托书）")
        self.model.to(device).eval()

    def classify(self, frame: RadarFrame) -> BehaviorPrediction:
        torch = self._torch
        sig = frame.signature
        if isinstance(sig, str) and os.path.isdir(sig):
            frames = load_mmwave_frames(sig)
            tensor = preprocess_sequence(frames)
        elif isinstance(sig, (list, tuple)):
            tensor = preprocess_sequence(list(sig))
        elif hasattr(sig, "shape") and len(sig.shape) == 4:
            tensor = sig
        else:
            raise ValueError("signature 需为 mmwave 目录路径、点云序列或预处理张量")

        with torch.no_grad():
            input_tensor = torch.from_numpy(tensor).float().unsqueeze(0).to(self.device)
            logits = self.model(input_tensor)
            probs = torch.softmax(logits, dim=1)[0]
            idx = int(probs.argmax())
            conf = float(probs[idx])
        action = MMFI_TO_BEHAVIOR.get(MMFI_ACTIONS[idx], BehaviorAction.normal_activity)
        return BehaviorPrediction(action=action, confidence=conf)
