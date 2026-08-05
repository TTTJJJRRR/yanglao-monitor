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
import re

import numpy as np

GRID = 32          # 每帧体素网格边长
T_FRAMES = 32      # 时间维采样帧数
XY_RANGE = (-3.0, 3.0)  # 米，按 IWR6843AOP 量程调整


def _frame_number(path: str) -> int:
    match = re.search(r"frame(\d+)", os.path.basename(path))
    return int(match.group(1)) if match else -1


def load_mmwave_frames(mmwave_dir: str) -> list[np.ndarray]:
    """读取一个样本的全体 mmwave 帧，返回 (N, 3) 点云列表（顺序=时间）。"""
    bins = sorted(glob.glob(os.path.join(mmwave_dir, "frame*.bin")), key=_frame_number)
    frames: list[np.ndarray] = []
    for path in bins:
        with open(path, "rb") as f:
            raw = f.read()
        if not raw:
            continue

        # MMFi 点云包通常是 float64；兼容常见的 float32 导出包，但不猜测
        # 点数或截断非完整点，避免把损坏帧静默当作有效输入。
        dtype = np.float64 if len(raw) % (3 * np.dtype(np.float64).itemsize) == 0 else np.float32
        values = np.frombuffer(raw, dtype=dtype)
        if values.size == 0 or values.size % 3:
            continue
        points = values.reshape(-1, 3).astype(np.float32, copy=False)
        points = points[np.isfinite(points).all(axis=1)]
        if len(points):
            frames.append(points)
    return frames


def voxelize_frame(points: np.ndarray, grid: int = GRID, xy_range=XY_RANGE) -> np.ndarray:
    """单帧点云 -> (2, grid, grid)：ch0 占据数(归一化)，ch1 平均高度。"""
    points = np.asarray(points, dtype=np.float32)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("每帧点云必须是形状 (N, 3) 的数组")

    occ = np.zeros((grid, grid), dtype=np.float32)
    hgt = np.zeros((grid, grid), dtype=np.float32)
    cnt = np.zeros((grid, grid), dtype=np.float32)
    if points.shape[0] == 0:
        return np.stack([occ, hgt], axis=0)
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    lo, hi = xy_range
    span = hi - lo
    valid = np.isfinite(points).all(axis=1)
    ix = ((x[valid] - lo) / span * grid).clip(0, grid - 1).astype(int)
    iy = ((y[valid] - lo) / span * grid).clip(0, grid - 1).astype(int)
    zv = z[valid]
    np.add.at(occ, (iy, ix), 1.0)
    np.add.at(hgt, (iy, ix), zv)
    np.add.at(cnt, (iy, ix), 1.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        hgt = np.where(cnt > 0, hgt / cnt, 0.0)
    occ = occ / (occ.max() + 1e-6)
    return np.stack([occ, hgt], axis=0)


def preprocess_sequence(
    frames: list[np.ndarray], grid: int = GRID, t_frames: int = T_FRAMES
) -> np.ndarray:
    """点云序列 -> (t_frames, 2, grid, grid)，不足部分零填充，超出部分均匀采样。"""
    if t_frames <= 0:
        raise ValueError("t_frames 必须大于 0")
    if not frames:
        return np.zeros((t_frames, 2, grid, grid), dtype=np.float32)

    if len(frames) > t_frames:
        selected = [frames[i] for i in np.linspace(0, len(frames) - 1, t_frames).astype(int)]
    else:
        selected = list(frames)
    seq = np.zeros((t_frames, 2, grid, grid), dtype=np.float32)
    for i, points in enumerate(selected):
        seq[i] = voxelize_frame(points, grid)
    return seq
