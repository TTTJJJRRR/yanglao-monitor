"""IWR6843AOP OOB TLV 帧解析与测试夹具生成工具。

此模块把 edge/capture_oob.py 里的已验证解析逻辑内聚到后端可导入的位置，
供 RadarPhaseProvider 与 fixture 测试共用。
"""
from __future__ import annotations

from dataclasses import dataclass
import struct
from typing import Iterable

import numpy as np

MAGIC = bytes([2, 1, 4, 3, 6, 5, 8, 7])
TLV_DETECTED_POINTS = 1
HDR_SIZE = 40


@dataclass(frozen=True)
class ParsedOobFrame:
    points: np.ndarray
    total_len: int


def parse_frame(buf: bytes, pos: int = 0) -> ParsedOobFrame | None:
    """解析一帧 OOB TLV，返回点云与帧长度。

    返回 None 表示当前缓冲区中缺少完整帧或帧头损坏。
    """
    if pos < 0 or pos + HDR_SIZE > len(buf):
        return None
    if buf[pos : pos + len(MAGIC)] != MAGIC:
        return None

    total_len = struct.unpack_from("<I", buf, pos + 12)[0]
    num_tlv = struct.unpack_from("<I", buf, pos + 32)[0]
    if total_len <= 0 or pos + total_len > len(buf):
        return None

    body = buf[pos + HDR_SIZE : pos + total_len]
    off = 0
    points: np.ndarray | None = None
    for _ in range(num_tlv):
        if off + 8 > len(body):
            break
        tlv_type, tlv_len = struct.unpack_from("<II", body, off)
        off += 8
        payload = body[off : off + tlv_len]
        off += tlv_len
        if tlv_type != TLV_DETECTED_POINTS or len(payload) < 4:
            continue
        n = struct.unpack_from("<I", payload, 0)[0]
        floats = np.frombuffer(payload[4 : 4 + n * 16], dtype="<f4")
        if floats.size == n * 4:
            points = floats.reshape(n, 4)[:, :3].astype(np.float32, copy=False)

    if points is None:
        points = np.zeros((0, 3), dtype=np.float32)
    return ParsedOobFrame(points=points, total_len=total_len)


def iter_frames(buf: bytes) -> list[np.ndarray]:
    """从连续字节流中提取所有完整点云帧。"""
    frames: list[np.ndarray] = []
    pos = 0
    while pos + HDR_SIZE <= len(buf):
        magic_at = buf.find(MAGIC, pos)
        if magic_at < 0:
            break
        parsed = parse_frame(buf, magic_at)
        if parsed is None:
            pos = magic_at + 1
            continue
        frames.append(parsed.points)
        pos = magic_at + parsed.total_len
    return frames


def build_detected_points_tlv(points: np.ndarray) -> bytes:
    """构造 TLV type=1 的检测点载荷（测试夹具用）。"""
    pts = np.asarray(points, dtype=np.float32)
    if pts.ndim != 2 or pts.shape[1] != 3:
        raise ValueError("points 必须是 (N, 3) 数组")
    payload = struct.pack("<I", pts.shape[0])
    doppler = np.zeros((pts.shape[0], 1), dtype=np.float32)
    data = np.concatenate([pts, doppler], axis=1).astype("<f4", copy=False)
    payload += data.tobytes()
    return struct.pack("<II", TLV_DETECTED_POINTS, len(payload)) + payload


def build_oob_frame(points: np.ndarray, frame_num: int = 1, timestamp_ms: int = 0) -> bytes:
    """构造单帧 OOB TLV 字节流（测试夹具用）。"""
    tlv = build_detected_points_tlv(points)
    total_len = HDR_SIZE + len(tlv)
    header = struct.pack(
        "<8sIIIIIIII",
        MAGIC,
        0x01020304,
        total_len,
        0xA1642,  # platform 占位，不参与解析
        frame_num,
        timestamp_ms,
        int(np.asarray(points).shape[0]),
        1,
        0,
    )
    return header + tlv


def build_oob_stream(frames: Iterable[np.ndarray]) -> bytes:
    """把多帧拼成连续 OOB 字节流。"""
    chunks = []
    for idx, pts in enumerate(frames, start=1):
        chunks.append(build_oob_frame(pts, frame_num=idx, timestamp_ms=idx * 50))
    return b"".join(chunks)
