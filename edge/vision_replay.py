"""视觉回放验证脚本（A2）：mp4 → MediaPipe Pose 关键点 → 跌倒分（负样本验证）。

用途：验证同学采集的「坐 / 走」视频，确认 `fall_score_from_keypoints` +
`FallDetector` 对正常动作**不误报跌倒**（负样本）。原始画面不上云，仅边缘本地处理。

依赖（仅边缘侧）：pip install mediapipe opencv-python
运行：
    python edge/vision_replay.py --video "C:/Users/tttt/Desktop/姿势/sitting/xxx.mp4"
    python edge/vision_replay.py --video "C:/Users/tttt/Desktop/姿势" --stride 5   # 目录=扫描所有 mp4

期望结果：坐/走视频的 fall_score 应整体偏低（<0.3），FallDetector 不应触发红色
（is_fall=False）。若出现红色，说明几何阈值/确认窗口对坐姿误报，需回调阈值。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 复用视觉节点的纯几何核心，保证两处口径一致
from vision_node import FallDetector, fall_score_from_keypoints

Keypoints = dict[int, tuple[float, float, float]]


def _landmarks_to_keypoints(landmarks) -> Keypoints:
    """MediaPipe Pose 33 关键点 -> {idx: (x, y, z)} 归一化坐标。"""
    return {i: (lm.x, lm.y, lm.z) for i, lm in enumerate(landmarks)}


def process_video(
    video: Path,
    stride: int = 5,
    max_frames: int = 0,
    detector: FallDetector | None = None,
) -> dict:
    """处理单个 mp4，返回统计。mediapipe/cv2 缺失时抛 ImportError。"""
    import cv2
    import mediapipe as mp

    det = detector or FallDetector(window_size=3, threshold=0.6)
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        return {"video": str(video), "error": "无法打开视频"}

    scores: list[float] = []
    red = 0
    yellow = 0
    frames_processed = 0
    frame_idx = 0

    with mp.solutions.pose.Pose(
        static_image_mode=False, model_complexity=1, min_detection_confidence=0.5
    ) as pose:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame_idx += 1
            if stride > 1 and (frame_idx - 1) % stride != 0:
                continue
            if max_frames and frames_processed >= max_frames:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)
            if not result.pose_landmarks:
                continue  # 无人/未检测到，跳过

            kpts = _landmarks_to_keypoints(result.pose_landmarks.landmark)
            score = fall_score_from_keypoints(kpts)
            verdict = det.update(score)
            scores.append(score)
            frames_processed += 1
            if verdict["is_fall"]:
                red += 1
            elif verdict["watch"]:
                yellow += 1

    cap.release()
    n = len(scores)
    return {
        "video": str(video),
        "frames_processed": frames_processed,
        "avg_fall_score": round(sum(scores) / n, 3) if n else None,
        "max_fall_score": round(max(scores), 3) if n else None,
        "red_alerts": red,
        "yellow_watch": yellow,
        "verdict": "PASS(未误报跌倒)" if red == 0 else "FAIL(出现跌倒红警，需回调阈值)",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="视觉回放负样本验证（坐/走不误报跌倒）")
    ap.add_argument("--video", required=True, help="单个 mp4 或目录（目录则扫描所有 mp4）")
    ap.add_argument("--stride", type=int, default=5, help="每隔 N 帧抽一帧（提速）")
    ap.add_argument("--max-frames", type=int, default=0, help="每视频最多处理帧数，0=不限")
    args = ap.parse_args()

    p = Path(args.video)
    videos = sorted(p.rglob("*.mp4")) if p.is_dir() else ([p] if p.exists() else [])
    if not videos:
        print(f"未找到 mp4：{args.video}")
        sys.exit(1)

    # 依赖检测前置，避免半途失败
    try:
        import cv2  # noqa: F401
        import mediapipe  # noqa: F401
    except ImportError as e:
        print(f"缺少依赖：{e.name}。请先 `pip install mediapipe opencv-python` 再跑。")
        print("（沙箱无摄像头/媒体库；本脚本在装有媒体库的边缘机运行。）")
        sys.exit(2)

    print(f"共 {len(videos)} 个视频，stride={args.stride}")
    for v in videos:
        try:
            r = process_video(v, stride=args.stride, max_frames=args.max_frames)
            print(
                f"- {Path(r['video']).name}: frames={r['frames_processed']} "
                f"avg={r['avg_fall_score']} max={r['max_fall_score']} "
                f"red={r['red_alerts']} yellow={r['yellow_watch']} -> {r['verdict']}"
            )
        except Exception as e:  # noqa: BLE001 - 单个视频失败不阻断整体
            print(f"- {v.name}: 处理失败 {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
