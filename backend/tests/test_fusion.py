"""雷达 + 视觉 跌倒融合决策测试（M3 评审命门，纯逻辑，可测）。

验证融合矩阵：
- 双模态一致(雷达跌倒高置信 + 视觉高跌倒分) -> 红警
- 仅雷达判定 -> 黄警
- 仅视觉判定 -> 黄警（视觉不上云，仅边缘辅助）
- 高置信行走/静止 -> 无报警，行为透传
- 雷达低置信(<0.6)且视觉低 -> 回落 still，绝不误报 falling
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

from app.inference.fall_fusion import fuse


def test_dual_modal_agree_red():
    r = fuse("falling", 0.9, 0.85, 0.9)
    assert r["is_fall"] is True
    assert r["alert_level"] == "red"
    assert r["action"] == "falling"


def test_radar_only_yellow():
    r = fuse("falling", 0.9, 0.1, 0.9)
    assert r["is_fall"] is True
    assert r["alert_level"] == "yellow"


def test_vision_only_yellow():
    r = fuse("walking", 0.9, 0.9, 0.9)
    assert r["is_fall"] is True
    assert r["alert_level"] == "yellow"
    assert r["action"] == "falling"


def test_high_conf_walking_no_alert():
    r = fuse("walking", 0.9, 0.1, 0.9)
    assert r["is_fall"] is False
    assert r["alert_level"] is None
    assert r["action"] == "walking"


def test_low_conf_radar_falls_back_to_still():
    # 雷达 conf<0.6 不能判定跌倒；视觉也低 -> 回落 still，绝不误报 falling
    r = fuse("falling", 0.4, 0.1, 0.2)
    assert r["is_fall"] is False
    assert r["action"] == "still"
    assert r["alert_level"] is None


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
