"""在 MMFi mmwave 模态上训练 MmWaveCNN（真实数据管线）。

数据：MMFi 解压根目录下 E*/S*/A*/mmwave/frame*.bin。
标签：A{act} 数字 -> 0..26（MMFI_ACTIONS 顺序，27 类）。
输出：weights.pt（与本模块同目录），供 MmWaveBehaviorCNN 加载。

运行（装有 torch 的环境，建议 GPU；Cursor 委托书里即此命令）：
    cd backend
    PYTHONPATH=. python -m backend.app.inference.mwave_cnn.train <MMFi解压根目录> \
        --epochs 30 --batch-size 16
"""
from __future__ import annotations

import argparse
import glob
import os

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from .preprocess import load_mmwave_frames, preprocess_sequence
from .model import MmWaveCNN
from .classifier import MMFI_ACTIONS


class MMFiMMWaveDataset(Dataset):
    def __init__(self, root: str, grid: int = 32, t_frames: int = 32):
        self.samples: list[tuple[list[np.ndarray], int]] = []
        for mm in glob.glob(os.path.join(root, "E*", "S*", "A*", "mmwave")):
            act = os.path.basename(os.path.dirname(mm))  # "Axx"
            if act not in MMFI_ACTIONS:
                continue
            label = MMFI_ACTIONS.index(act)
            frames = load_mmwave_frames(mm)
            if len(frames) == 0:
                continue
            self.samples.append((frames, label))
        self.grid, self.t_frames = grid, t_frames

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, i):
        frames, label = self.samples[i]
        x = preprocess_sequence(frames, self.grid, self.t_frames)
        return torch.from_numpy(x), label


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset_root", help="MMFi 解压根目录")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "weights.pt"))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    ds = MMFiMMWaveDataset(args.dataset_root)
    print(f"[train] loaded {len(ds)} mmwave samples across {len(MMFI_ACTIONS)} classes")
    if len(ds) == 0:
        raise SystemExit("未找到 mmwave 样本，请确认 dataset_root 下存在 E*/S*/A*/mmwave/frame*.bin")
    dl = DataLoader(ds, batch_size=args.batch_size, shuffle=True, num_workers=0)

    model = MmWaveCNN(num_classes=len(MMFI_ACTIONS)).to(args.device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    crit = nn.CrossEntropyLoss()
    model.train()
    for ep in range(args.epochs):
        tot = 0.0
        n = 0
        for x, y in dl:
            x, y = x.to(args.device), y.to(args.device)
            opt.zero_grad()
            loss = crit(model(x), y)
            loss.backward()
            opt.step()
            tot += loss.item() * x.size(0)
            n += x.size(0)
        print(f"[train] epoch {ep + 1}/{args.epochs} loss={tot / n:.4f}")
    torch.save(model.state_dict(), args.out)
    print(f"[train] saved weights -> {args.out}")


if __name__ == "__main__":
    main()
