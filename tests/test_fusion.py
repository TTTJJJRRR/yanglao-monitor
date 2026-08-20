import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

from app.inference.fall_fusion import fuse
from app.models import BehaviorAction


def test_dual_modal_agree_red():
    r = fuse("falling", 0.9, 0.85, 0.9)
    assert r["is_fall"] is True
    assert r["alert_level"] == "red"
    assert r["action"] == "falling"


def test_low_conf_crouching_should_watch():
    r = fuse(BehaviorAction.crouching.value, 0.4, 0.1, 0.2)
    assert r["is_fall"] is False
    assert r["needs_review"] is True


def test_low_conf_unknown_should_watch():
    r = fuse(BehaviorAction.normal_activity.value, 0.4, 0.1, 0.2)
    assert r["is_fall"] is False
    assert r["needs_review"] is True
    assert r["action"] == BehaviorAction.normal_activity.value


def test_high_conf_walking_no_alert():
    r = fuse("walking", 0.9, 0.1, 0.9)
    assert r["is_fall"] is False
    assert r["needs_review"] is False
    assert r["action"] == "walking"


if __name__ == "__main__":
    test_dual_modal_agree_red()
    test_low_conf_crouching_should_watch()
    test_low_conf_unknown_should_watch()
    test_high_conf_walking_no_alert()
    print("ALL TESTS PASSED")
