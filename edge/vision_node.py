"""边缘视觉节点骨架（运行在树莓派 / Jetson 等边缘设备）。

当前为占位：周期性生成 mock 姿态跌倒分数并 POST 到后端 /api/edge/pose。
M2 接入：用 MediaPipe Pose 提取 33 个关键点，计算躯干-地面夹角与质心高度，
得到 fall_score（0~1），替换下方 mock 生成逻辑。视觉原始画面不上云（R-P0-03）。

依赖（M2 安装，仅在边缘侧）：
    pip install mediapipe requests

运行：
    python edge/vision_node.py [--backend http://localhost:8000] [--interval 2.0]
"""
import argparse
import random
import time

try:
    import requests
except ImportError:
    requests = None


def mock_fall_score() -> float:
    """占位：随机给出视觉跌倒分数（0~1）。M2 替换为 MediaPipe 计算。"""
    # TODO(M2): 用 MediaPipe Pose 关键点计算真实 fall_score
    return round(random.uniform(0.0, 0.3), 2)


def main() -> None:
    parser = argparse.ArgumentParser(description="康养边缘视觉节点（占位骨架）")
    parser.add_argument("--backend", default="http://localhost:8000", help="后端地址")
    parser.add_argument("--interval", type=float, default=2.0, help="推送间隔（秒）")
    args = parser.parse_args()

    if requests is None:
        print("缺少 requests 库，请先 pip install requests")
        return

    print(f"视觉节点启动，推送至 {args.backend}/api/edge/pose（每 {args.interval}s 一次）")
    while True:
        payload = {
            "device_id": "CAM_01",
            "fall_score": mock_fall_score(),
            "confidence": round(random.uniform(0.6, 0.95), 2),
        }
        try:
            requests.post(f"{args.backend}/api/edge/pose", json=payload, timeout=5)
        except Exception as e:  # noqa: BLE001 - 边缘侧网络抖动需容忍
            print(f"推送失败: {e}")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
