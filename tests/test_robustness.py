import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

from app.inference.fall_fusion import fuse
from app.models import BehaviorAction


def test_fusion_handles_none_inputs():
    r = fuse(None, 0.0, 0.0, 0.0)
    assert r["action"] == BehaviorAction.normal_activity.value
    assert r["needs_review"] is True


if __name__ == "__main__":
    test_fusion_handles_none_inputs()
    print("ALL TESTS PASSED")
