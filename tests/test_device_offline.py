import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

from app.monitoring import DeviceMonitor


class FakeClock:
    def __init__(self, start_ms: int = 0):
        self.now = start_ms

    def __call__(self) -> int:
        return self.now

    def advance(self, ms: int) -> None:
        self.now += ms


def test_offline_then_online_recovery():
    clock = FakeClock(0)
    monitor = DeviceMonitor(timeout_s=5.0, now_ms=clock)
    monitor.touch("radar", 100)
    clock.advance(6000)
    events = monitor.check()
    assert len(events) == 1
    assert events[0]["type"] == "device_offline"
    assert events[0]["data"]["level"] == "critical"

    monitor.touch("radar", 7000)
    events = monitor.check()
    assert len(events) == 1
    assert events[0]["type"] == "device_online"


if __name__ == "__main__":
    test_offline_then_online_recovery()
    print("ALL TESTS PASSED")
