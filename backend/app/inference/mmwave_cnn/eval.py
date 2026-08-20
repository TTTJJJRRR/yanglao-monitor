"""MMWave CNN 评估脚本（M5 训练/评估脚手架）。

无 sklearn 依赖，仅用 numpy 输出每类准确率与混淆矩阵。
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch

from .classifier import MmWaveBehaviorCNN
from .dataset import RadarDataset, LABEL_TO_INDEX
from .preprocess import preprocess_sequence


def _confusion_matrix(y_true: list[int], y_pred: list[int], n_classes: int) -> np.ndarray:
    mat = np.zeros((n_classes, n_classes), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        mat[t, p] += 1
    return mat


def evaluate(weights: str, dataset_root: str, num_classes: int = 8) -> dict:
    dataset = RadarDataset(dataset_root)
    if len(dataset) == 0:
        raise SystemExit("未找到可评估数据")
    model = MmWaveBehaviorCNN(weights_path=weights, num_classes=27)
    model.model.eval()

    y_true: list[int] = []
    y_pred: list[int] = []
    with torch.no_grad():
        for sample in dataset:
            tensor = torch.from_numpy(preprocess_sequence(sample.frames)).float()
            pred = model.classify(type("Frame", (), {"signature": tensor, "device_id": "RADAR_01", "timestamp_ms": 0})())
            y_true.append(LABEL_TO_INDEX[sample.label])
            y_pred.append(LABEL_TO_INDEX.get(pred.action, 0))

    cm = _confusion_matrix(y_true, y_pred, num_classes)
    per_class = {}
    for idx in range(num_classes):
        total = cm[idx].sum()
        per_class[idx] = float(cm[idx, idx] / total) if total else None
    return {"per_class_accuracy": per_class, "confusion_matrix": cm}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset_root")
    ap.add_argument("--weights", default=str(Path(__file__).with_name("weights.pt")))
    args = ap.parse_args()
    result = evaluate(args.weights, args.dataset_root)
    print("per_class_accuracy:")
    for idx, acc in result["per_class_accuracy"].items():
        print(f"  {idx}: {acc if acc is not None else '待评估'}")
    print("confusion_matrix:")
    print(result["confusion_matrix"])


if __name__ == "__main__":
    main()
