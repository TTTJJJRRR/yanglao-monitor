"""真实生命体征估计算法测试（纯 Python，无第三方依赖，可在沙箱直接跑）。

验证点：
- 合成已知频率(呼吸 15 次/分、心率 66 bpm)信号 -> 真实周期图算法应恢复出 ~15.0 / ~66.0
- 空/过短信号 -> 返回 None 且 motion_flag=True（不伪造）
- 合成源 MmVitalSource.next_vital() 返回真实估计（非随机假数据）
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

from app.sources.mmvital_estimator import estimate_vitals, synthesize_chest_signal, MmVitalEstimator
from app.sources.mmvital_source import MmVitalSource, SyntheticPhaseProvider


def test_recovers_known_frequencies():
    # 呼吸 15 次/分 = 0.25 Hz；心率 66 bpm = 1.1 Hz（与默认 SyntheticPhaseProvider 一致）
    sig = synthesize_chest_signal(0.25, 1.1, fs=20.0, duration_s=5.0, noise=0.05, seed=7)
    est = estimate_vitals(sig, fs=20.0)
    assert est.breath_rate is not None and abs(est.breath_rate - 15.0) < 1.0, est
    assert est.heart_rate is not None and abs(est.heart_rate - 66.0) < 1.0, est
    assert est.quality > 0.0
    assert est.motion_flag is False


def test_short_signal_is_motion():
    est = estimate_vitals([1.0, 2.0], fs=20.0)
    assert est.breath_rate is None
    assert est.heart_rate is None
    assert est.motion_flag is True


def test_synthetic_source_returns_real_estimate():
    src = MmVitalSource(
        fs=20.0,
        provider=SyntheticPhaseProvider(fs=20.0, breath_hz=0.25, heart_hz=1.1, seed=7),
    )
    frame = src.next_vital()
    assert frame is not None
    assert frame["source"] == "real"
    assert abs(frame["breath_rate"] - 15.0) < 1.0, frame
    assert abs(frame["heart_rate"] - 66.0) < 1.0, frame


def test_estimator_equivalent_to_function():
    sig = synthesize_chest_signal(0.25, 1.1, fs=20.0, duration_s=5.0, noise=0.05, seed=7)
    e1 = MmVitalEstimator(fs=20.0).estimate(sig)
    e2 = estimate_vitals(sig, fs=20.0)
    assert e1.breath_rate == e2.breath_rate
    assert e1.heart_rate == e2.heart_rate


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
