"""雷达行为 CNN（PyTorch）。

Baseline：逐帧 2D CNN 提取空间特征 -> 时序平均池 -> 分类头。
思想移植自 radar-lab/patient_monitoring 的 3 层 CNN（原 ROS/TensorFlow，
此处用 PyTorch 重实现，因为上游无公开权重、无公开数据）。

输入: (B, T, 2, H, W)  输出: (B, num_classes) logits
num_classes 默认 27，对应 MMFi 的 27 个动作类（项目不止跌倒，活动监测全覆盖）。
"""
from __future__ import annotations

import torch
import torch.nn as nn


class MmWaveCNN(nn.Module):
    def __init__(self, num_classes: int = 27, grid: int = 32, t_frames: int = 32):
        super().__init__()
        self.t_frames = t_frames
        self.backbone = nn.Sequential(
            nn.Conv2d(2, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d(1),
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64, 64), nn.ReLU(),
            nn.Linear(64, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, 2, H, W)
        B, T, C, H, W = x.shape
        x = x.reshape(B * T, C, H, W)
        feat = self.backbone(x)        # (B*T, 64, 1, 1)
        feat = feat.reshape(B, T, -1)  # (B, T, 64)
        feat = feat.mean(dim=1)        # 时序平均池 -> (B, 64)
        return self.head(feat)         # (B, num_classes)
