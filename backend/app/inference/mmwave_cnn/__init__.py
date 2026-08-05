"""mmWave 行为 CNN 子包：真实雷达行为识别（MMFi 数据训练）。"""
from .classifier import MmWaveBehaviorCNN, MMFI_ACTIONS, MMFI_TO_BEHAVIOR
from .model import MmWaveCNN
from .preprocess import load_mmwave_frames, preprocess_sequence, voxelize_frame

__all__ = [
    "MmWaveBehaviorCNN",
    "MMFI_ACTIONS",
    "MMFI_TO_BEHAVIOR",
    "MmWaveCNN",
    "load_mmwave_frames",
    "preprocess_sequence",
    "voxelize_frame",
]
