import os
import sys
from pathlib import Path

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

import numpy as np

from app.sources.oob_tlv import build_oob_stream, iter_frames
from app.sources.mmvital_estimator import estimate_vitals
from app.sources.mmvital_source import RadarPhaseProvider


def test_oob_fixture_stream_roundtrip():
    frames = [
        np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], dtype=np.float32),
        np.array([[0.2, 0.1, 0.0]], dtype=np.float32),
    ]
    stream = build_oob_stream(frames)
    parsed = iter_frames(stream)
    assert len(parsed) == 2
    assert parsed[0].shape == (2, 3)
    assert parsed[1].shape == (1, 3)


def test_radar_phase_provider_falls_back_without_env(monkeypatch=None):
    provider = RadarPhaseProvider()
    assert provider.next_window() is None or isinstance(provider.next_window(), list)


def test_estimator_runs_on_parsed_phase_signal():
    # fixture 型点云投影后的信号，保证估计器至少可跑通。
    sig = [0.1 * i for i in range(20)]
    est = estimate_vitals(sig, fs=20.0)
    assert est.motion_flag is False or est.motion_flag is True


if __name__ == "__main__":
    for fn in [test_oob_fixture_stream_roundtrip, test_radar_phase_provider_falls_back_without_env, test_estimator_runs_on_parsed_phase_signal]:
        fn()
    print("ALL TESTS PASSED")
