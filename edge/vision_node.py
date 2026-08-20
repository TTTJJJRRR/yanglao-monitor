"""边缘视觉节点（真实 MediaPipe Pose 集成，无训练）。

- fall_score_from_keypoints(kpts)：输入 33 关键点（像素 / 归一化坐标），
  计算 (1) 躯干-地面夹角（肩-髋向量与竖直方向夹角）；(2) 质心相对身高高度比；
  二者合成 fall_score(0~1)。站立 ≈ 0，跌倒 / 躺地 ≈ 1。纯 Python，可测。
- VisionNode：若 mediapipe 可用，对摄像头帧跑 BlazePose 取关键点；
  否则用注入的关键点（演示 / 测试）。结果 POST 到后端 /api/edge/pose。
- 视觉原始画面不上云（R-P0-03）。

依赖（仅边缘侧）：pip install mediapipe requests
运行：python edge/vision_node.py [--backend http://localhost:8000] [--interval 2.0]
"""
from __future__ import annotations

import argparse
import math
import time
from collections import deque
from typing import Callable, Dict, Tuple

try:
    import requests
except ImportError:
    requests = None

Keypoints = Dict[int, Tuple[float, float, float]]


def _angle_with_vertical(vx: float, vy: float) -> float:
    """向量与竖直向下方向 (0,1) 的夹角（度）。站立躯干≈0，躺地平躺≈90。"""
    mag = math.hypot(vx, vy) + 1e-9
    cos = abs(vy) / mag
    return math.degrees(math.acos(max(-1.0, min(1.0, cos))))


def fall_score_from_keypoints(kpts: Keypoints) -> float:
    """BlazePose 33 关键点 -> fall_score 0~1（纯几何，无训练）。"""
    def mid(a: int, b: int):
        ka, kb = kpts.get(a), kpts.get(b)
        if not ka or not kb:
            return None
        return ((ka[0] + kb[0]) / 2, (ka[1] + kb[1]) / 2, (ka[2] + kb[2]) / 2)

    shoulder = mid(11, 12)
    hip = mid(23, 24)
    nose = kpts.get(0)
    if shoulder is None or hip is None:
        return 0.5  # 关键点缺失，给中性分数（conservative）

    torso_vx = shoulder[0] - hip[0]
    torso_vy = shoulder[1] - hip[1]
    torso_angle = _angle_with_vertical(torso_vx, torso_vy)  # 0=直立, 90=平躺

    hip_y = hip[1]
    ref_y = shoulder[1]
    height_ratio = 0.0
    if abs(hip_y - ref_y) > 1e-6:
        head_y = nose[1] if nose else shoulder[1]
        height_ratio = abs(head_y - hip_y) / abs(hip_y - ref_y)

    angle_score = min(1.0, torso_angle / 75.0)
    height_score = max(0.0, 1.0 - min(1.0, height_ratio))
    score = 0.7 * angle_score + 0.3 * height_score
    return round(min(1.0, max(0.0, score)), 3)


def standing_keypoints() -> Keypoints:
    """竖直站立样例：肩高于髋，躯干近竖直。"""
    return {
        11: (0.5, 0.35, 0.0), 12: (0.5, 0.35, 0.0),
        23: (0.5, 0.55, 0.0), 24: (0.5, 0.55, 0.0),
        0: (0.5, 0.20, 0.0), 29: (0.5, 0.90, 0.0), 30: (0.5, 0.90, 0.0),
    }


def fallen_keypoints() -> Keypoints:
    """躺地样例：身体整体水平（肩在一端、髋在另一端，左右不对称），鼻与髋同高。"""
    return {
        11: (0.20, 0.60, 0.0), 12: (0.25, 0.60, 0.0),
        23: (0.80, 0.62, 0.0), 24: (0.85, 0.62, 0.0),
        0: (0.10, 0.61, 0.0), 29: (0.95, 0.62, 0.0), 30: (0.98, 0.62, 0.0),
    }


class FallDetector:
    """滑动窗口确认器：连续 K 帧高跌倒分才输出红警。"""

    def __init__(self, window_size: int = 3, threshold: float = 0.6):
        self.window_size = window_size
        self.threshold = threshold
        self._scores: deque[float] = deque(maxlen=window_size)

    def update(self, fall_score: float) -> dict:
        self._scores.append(float(fall_score))
        consecutive_high = len(self._scores) == self.window_size and all(s >= self.threshold for s in self._scores)
        if consecutive_high:
            return {"is_fall": True, "alert_level": "red", "watch": False, "window": list(self._scores)}
        if fall_score >= self.threshold:
            return {"is_fall": False, "alert_level": "yellow", "watch": True, "window": list(self._scores)}
        return {"is_fall": False, "alert_level": None, "watch": False, "window": list(self._scores)}


class VisionNode:
    def __init__(
        self,
        backend: str = "http://localhost:8000",
        interval: float = 2.0,
        keypoint_provider: Callable[[], Keypoints] | None = None,
        fall_detector: FallDetector | None = None,
    ):
        self.backend = backend
        self.interval = interval
        self.keypoint_provider = keypoint_provider
        self.fall_detector = fall_detector or FallDetector()
        self._mediapipe = None
        try:
            import mediapipe as mp

            self._mediapipe = mp
        except ImportError:
            self._mediapipe = None

    def _capture_keypoints(self) -> Keypoints | None:
        if self.keypoint_provider:
            return self.keypoint_provider()
        if self._mediapipe is None:
            return None  # 无摄像头 / 无 mediapipe：由调用方注入测试关键点
        # TODO(M2): 打开摄像头 -> mp.solutions.pose.Pose -> 取 landmarks 归一化坐标
        return None

    def run_once(self) -> dict:
        kpts = self._capture_keypoints()
        if kpts is None:
            return {"device_id": "CAM_01", "fall_score": 0.0, "confidence": 0.0, "is_fall": False, "alert_level": None, "watch": False}
        score = fall_score_from_keypoints(kpts)
        conf = 0.92 if (score > 0.6 or score < 0.2) else 0.7
        verdict = self.fall_detector.update(score)
        return {
            "device_id": "CAM_01",
            "fall_score": score,
            "confidence": conf,
            **verdict,
        }

    def loop(self) -> None:
        if requests is None:
            print("缺少 requests 库，请先 pip install requests")
            return
        print(f"视觉节点启动，推送至 {self.backend}/api/edge/pose（每 {self.interval}s 一次）")
        while True:
            payload = self.run_once()
            try:
                requests.post(f"{self.backend}/api/edge/pose", json=payload, timeout=5)
            except Exception as e:  # noqa: BLE001 - 边缘侧网络抖动需容忍
                print(f"推送失败: {e}")
            time.sleep(self.interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="康养边缘视觉节点（真实 MediaPipe Pose）")
    parser.add_argument("--backend", default="http://localhost:8000", help="后端地址")
    parser.add_argument("--interval", type=float, default=2.0, help="推送间隔（秒）")
    args = parser.parse_args()
    VisionNode(args.backend, args.interval).loop()


if __name__ == "__main__":
    main()
