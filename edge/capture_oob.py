"""IWR6843AOP out-of-box 点云采集脚本（真实数据管线入口）。

连 DATA UART -> 解析 mmWave OOB demo 的 TLV 帧 -> 每帧点云存成 (N,3) float64 .bin
（格式与 MMFi 的 mmwave 模态完全一致，backend 的 load_mmwave_frames 可直接读，train.py 零改动）。

⚠️ 版本敏感：魔数 / TLV 头按 TI mmWave SDK OOB demo 标准布局写，但不同 SDK 版本
   字段偏移可能微调。若首帧解析不出点，请对照你 SDK 的 mmw_output.h 校正 MAGIC / 偏移。

采集机依赖：pyserial, numpy（不进后端 venv，单独装即可）。
"""
from __future__ import annotations

import argparse
import os
import struct
import sys
import time

try:
    import serial
except ImportError:
    sys.exit("请先装 pyserial: pip install pyserial")

import numpy as np

# 标准 OOB demo 魔数（与 mmWave Demo Visualizer 同款字节序）
MAGIC = bytes([2, 1, 4, 3, 6, 5, 8, 7])
TLV_DETECTED_POINTS = 1

# OOB demo 帧头布局（xWR68xx）：
#   magic(8) + version(4) + totalLen(4) + platform(4) + frameNum(4)
#   + timeCpu(4) + numObj(4) + numTLVs(4) + subFrame(4)  = 40 bytes
HDR_SIZE = 40


def parse_frame(buf: bytes, pos: int):
    """从 pos(魔数起点) 解析一帧，返回 (points_xyz: np.ndarray(N,3)|None, frame_len)。"""
    if pos + HDR_SIZE > len(buf):
        return None, 0
    total_len = struct.unpack_from("<I", buf, pos + 8)[0]
    num_tlv = struct.unpack_from("<I", buf, pos + 32)[0]
    if total_len <= 0 or pos + total_len > len(buf):
        return None, total_len
    body = buf[pos + HDR_SIZE : pos + total_len]
    off = 0
    points = None
    for _ in range(num_tlv):
        if off + 8 > len(body):
            break
        tlv_type, tlv_len = struct.unpack_from("<II", body, off)
        off += 8
        payload = body[off : off + tlv_len]
        off += tlv_len
        if tlv_type == TLV_DETECTED_POINTS:
            # payload: numObj(4) + numObj*(x,y,z,doppler float32)
            if len(payload) < 4:
                continue
            n = struct.unpack_from("<I", payload, 0)[0]
            floats = np.frombuffer(payload[4 : 4 + n * 16], dtype="<f4")
            if floats.size == n * 4:
                points = floats.reshape(n, 4)[:, :3].astype(np.float64)
    return points, total_len


def main() -> None:
    ap = argparse.ArgumentParser(description="IWR6843AOP OOB 点云采集")
    ap.add_argument("--port", required=True, help="DATA UART 口，如 COM5 / /dev/ttyUSB1")
    ap.add_argument("--baud", type=int, default=921600)
    ap.add_argument("--out", required=True, help="输出目录，如 data/radar/E01/S01/A01/mmwave")
    ap.add_argument("--seconds", type=float, default=30.0)
    ap.add_argument("--max-frames", type=int, default=0, help="0=不限制")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    ser = serial.Serial(args.port, args.baud, timeout=0.5)
    print(f"[采集] 打开 {args.port}@{args.baud}，输出 {args.out}")

    buf = b""
    frame_idx = 0
    start = time.time()
    try:
        while True:
            chunk = ser.read(4096)
            if chunk:
                buf += chunk
            # 解析所有完整帧
            while True:
                i = buf.find(MAGIC)
                if i < 0:
                    break
                points, flen = parse_frame(buf, i)
                if flen <= 0:
                    break  # 帧未收全，等更多数据
                if points is not None and len(points) > 0:
                    path = os.path.join(args.out, f"frame{frame_idx:04d}.bin")
                    points.tofile(path)  # 默认 float64，匹配 MMFi
                    frame_idx += 1
                buf = buf[i + flen :]
            if args.max_frames and frame_idx >= args.max_frames:
                break
            if time.time() - start > args.seconds:
                break
    finally:
        ser.close()
    print(f"[采集] 完成，共 {frame_idx} 帧 -> {args.out}")


if __name__ == "__main__":
    main()
