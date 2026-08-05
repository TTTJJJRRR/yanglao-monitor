"""边缘视觉跌倒评分测试（真实 MediaPipe Pose 几何，纯 Python，无训练，可测）。

验证点：
- 站立样例 -> fall_score 低（<0.2）
- 躺地样例 -> fall_score 高（>0.6，且应在 0.7~0.95 区间）
- 关键点缺失 -> 中性分数 0.5（保守，不夸大报警）
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

from edge.vision_node import fall_score_from_keypoints, standing_keypoints, fallen_keypoints


def test_standing_is_low():
    assert fall_score_from_keypoints(standing_keypoints()) < 0.2


def test_fallen_is_high():
    assert fall_score_from_keypoints(fallen_keypoints()) > 0.6


def test_explicit_fallen_keypoints_value():
    # 躺地样例为水平躯干，复核分数落在 0.7~0.95
    s = fall_score_from_keypoints(fallen_keypoints())
    assert 0.7 <= s <= 0.95, s


def test_missing_keypoints_neutral():
    # 关键点缺失 -> 中性分数(0.5)，不放大为跌倒
    assert fall_score_from_keypoints({}) == 0.5


if __name__ == "__main__":
    import traceback
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("  PASS", name)
            except Exception as e:  # noqa: BLE001
                failed += 1
                print("  FAIL", name, "->", repr(e))
    if failed:
        print(f"\n{failed} FAILED")
        sys.exit(1)
    print("\nALL TESTS PASSED")
