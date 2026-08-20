import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

from edge.vision_node import FallDetector


def test_single_spike_no_red():
    detector = FallDetector(window_size=3, threshold=0.6)
    out1 = detector.update(0.1)
    out2 = detector.update(0.8)
    out3 = detector.update(0.1)
    assert out1["is_fall"] is False
    assert out2["alert_level"] == "yellow"
    assert out3["is_fall"] is False
    assert out3["alert_level"] is None


def test_three_consistent_high():
    detector = FallDetector(window_size=3, threshold=0.6)
    detector.update(0.8)
    detector.update(0.8)
    out3 = detector.update(0.8)
    assert out3["is_fall"] is True
    assert out3["alert_level"] == "red"


def test_alternating_no_red():
    detector = FallDetector(window_size=3, threshold=0.6)
    outputs = [detector.update(v) for v in [0.2, 0.8, 0.2, 0.8, 0.2]]
    assert all(o["is_fall"] is False for o in outputs)
    assert any(o["alert_level"] == "yellow" for o in outputs)


if __name__ == "__main__":
    test_single_spike_no_red()
    test_three_consistent_high()
    test_alternating_no_red()
    print("ALL TESTS PASSED")
