"""MMFi mmwave 点云序列 -> 固定张量 的预处理（真实数据管线）。

MMFi 的 mmwave 模态：每样本 297 帧，每帧一个 .bin ->
    np.frombuffer(raw, float64).reshape(-1, 3) = (N, 3) 点云 (x, y, z, 单位米)。
本模块把每帧体素化成 2 通道图（ch0=占据数归一化, ch1=平均高度），
沿时间均匀采样 T 帧 -> (T, 2, H, W)。

这是 baseline 表征。更优表征（微多普勒谱 / PointNet / 时序 3D CNN）留给训练阶段调优。
"""
from __future__ import annotations

import glob
import os

import numpy as np

GRID = 32          # 每帧体素网格边长
T_FRAMES = 32      # 时间维采样帧数
XY_RANGE = (-3.0, 3.0)  # 米，按 IWR6843AOP 量程调整


def load_mmwave_frames(mmwave_dir: str) -> list[np.ndarray]:
    """读取一个样本的全体 mmwave 帧，返回 (N, 3) 点云列表（顺序=时间）。"""
    bins = sorted(glob.glob(os.path.join(mmwave_dir, "frame*.bin")))
    frames: list[np.ndarray] = []
    for b in bins:
        with open(b, "rb") as f:
            raw = f.read()
        if not raw:
            continue
        pts = np.frombuffer(raw, dtype=np.float64).reshape(-1, 3)
        if pts.shape[0] > 0:
            frames.append(pts)
    return frames


def voxelize_frame(points: np.ndarray, grid: int = GRID, xy_range=XY_RANGE) -> np.ndarray:
    """单帧点云 -> (2, grid, grid)：ch0 占据数(归一化)，ch1 平均高度。"""
    occ = np.zeros((grid, grid), dtype=np.float32)
    hgt = np.zeros((grid, grid), dtype=np.float32)
    cnt = np.zeros((grid, grid), dtype=np.float32)
    if points.shape[0] == 0:
        return np.stack([occ, hgt], axis=0)
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    lo, hi = xy_range
    span = hi - lo
    ix = ((x - lo) / span * grid).clip(0, grid - 1).astype(int)
    iy = ((y - lo) / span * grid).clip(0, grid - 1).astype(int)
    for i in range(points.shape[0]):
        occ[iy[i], ix[i]] += 1.0
        hgt[iy[i], ix[i]] += z[i]
        cnt[iy[i], ix[i]] += 1.0
    with np.errstate(invalid="ignore", divide="ignore"):
        hgt = np.where(cnt > 0, hgt / cnt, 0.0)
    occ = occ / (occ.max() + 1e-6)
    return np.stack([occ, hgt], axis=0)


def preprocess_sequence(
    frames: list[np.ndarray], grid: int = GRID, t_frames: int = T_FRAMES
) -> np.ndarray:
    """点云序列 -> (t_frames, 2, grid, grid)。帧数不足零填充，过多均匀采样。"""
    if not frames:
        return np.zeros((t_frames, 2, grid, grid), dtype=np.float32)
    idx = np.linspace(0, len(frames) - 1, t_frames).astype(int)
    seq = np.stack([voxelize_frame(frames[i], grid) for i in idx], axis=0)
    return seq.astype(np.float32)
