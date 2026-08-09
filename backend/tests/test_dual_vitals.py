"""双估计器投票(DFT + EEMD)单元测试（纯 Python,无 numpy/pytest 依赖）。

覆盖:
1. vote() 四态确定性单测 —— 一致 / 分歧 / DFT缺检 / 质量过低。
2. estimate_dual() 集成 —— 已知频合成信号两法一致→high quality;纯噪声→不可信转盯防。

运行: 从 backend/ 目录 `python tests/test_dual_vitals.py`(pytest 未装也能跑)。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/

from app.sources.mmvital_estimator import VitalEstimate, synthesize_chest_signal
from app.sources.dual_vitals import vote, estimate_dual

_FAILS = []


def _check(name, cond, detail=""):
    status = "OK " if cond else "FAIL"
    print(f"[{status}] {name}" + (f"  -> {detail}" if detail and not cond else ""))
    if not cond:
        _FAILS.append(name)


def _test_vote_unit():
    # ③ 一致:两法都过质量门槛且频率接近 → agreement, quality 加成, 取均值
    dft = VitalEstimate(15.0, 66.0, False, 0.88)
    eemd = VitalEstimate(15.2, 65.5, False, 0.668)
    r = vote(dft, eemd)
    _check("vote:agree_flag", r.agreement is True)
    _check("vote:agree_breath_avg", r.breath_rate == 15.1, f"got {r.breath_rate}")
    _check("vote:agree_heart_avg", r.heart_rate == 65.8, f"got {r.heart_rate}")
    _check("vote:agree_quality_boosted", r.quality >= 0.88, f"got {r.quality}")
    _check("vote:agree_no_review", r.needs_review is False)

    # ④ 分歧:频率偏差超容忍 → 降可信 + 盯防
    dft2 = VitalEstimate(15.0, 66.0, False, 0.88)
    eemd2 = VitalEstimate(22.0, 95.0, False, 0.7)
    r2 = vote(dft2, eemd2)
    _check("vote:disagree_flag", r2.agreement is False)
    _check("vote:disagree_review", r2.needs_review is True)
    _check("vote:disagree_reason", r2.watch_reason is not None)
    _check("vote:disagree_quality_penalized", r2.quality < min(0.88, 0.7), f"got {r2.quality}")

    # ① DFT 缺检 → 退回 EEMD, 转盯防
    dft3 = VitalEstimate(None, None, True, 0.0)
    eemd3 = VitalEstimate(15.0, 66.0, False, 0.6)
    r3 = vote(dft3, eemd3)
    _check("vote:dft_none_flag", r3.agreement is False)
    _check("vote:dft_none_fallback", r3.breath_rate == 15.0 and r3.heart_rate == 66.0)
    _check("vote:dft_none_review", r3.needs_review is True)

    # ② 质量过低(频率接近但质量 < MIN_QUALITY)→ 不可信, 不误报一致
    dft4 = VitalEstimate(15.0, 66.0, False, 0.10)
    eemd4 = VitalEstimate(15.1, 66.0, False, 0.12)
    r4 = vote(dft4, eemd4)
    _check("vote:lowq_not_agree", r4.agreement is False)
    _check("vote:lowq_review", r4.needs_review is True)
    _check("vote:lowq_reason_low", "质量过低" in (r4.watch_reason or ""), f"got {r4.watch_reason}")
    _check("vote:lowq_penalized", r4.quality < 0.2, f"got {r4.quality}")

    # ⑤ 短窗口:EEMD 呼吸不可靠(breath_rate=None),但心率一致 → 仍判一致,呼吸取 DFT
    dft5 = VitalEstimate(15.0, 66.0, False, 0.88)
    eemd5 = VitalEstimate(None, 65.5, False, 0.668)  # 呼吸被降级为 None
    r5 = vote(dft5, eemd5)
    _check("vote:shortwin_agree", r5.agreement is True)
    _check("vote:shortwin_breath_from_dft", r5.breath_rate == 15.0, f"got {r5.breath_rate}")
    _check("vote:shortwin_no_review", r5.needs_review is False)


def _test_estimate_dual_integration():
    fs = 20.0
    # 已知:呼吸 0.25 Hz = 15 次/分;心率 1.10 Hz = 66 bpm
    sig = synthesize_chest_signal(
        breath_hz=0.25, heart_hz=1.10, fs=fs, duration_s=20.0, noise=0.05, seed=7
    )
    r = estimate_dual(sig, fs)
    _check("dual:synthetic_agree", r.agreement is True, f"reason={r.watch_reason}")
    _check("dual:synthetic_breath", r.breath_rate is not None and abs(r.breath_rate - 15.0) <= 1.0, f"got {r.breath_rate}")
    _check("dual:synthetic_heart", r.heart_rate is not None and abs(r.heart_rate - 66.0) <= 1.5, f"got {r.heart_rate}")
    _check("dual:synthetic_quality_high", r.quality >= 0.88, f"got {r.quality}")
    _check("dual:synthetic_no_review", r.needs_review is False)
    print(f"    合成: breath={r.breath_rate} heart={r.heart_rate} quality={r.quality} agree={r.agreement}")

    # 纯噪声:两法都应判不可信 → 转盯防
    rng = 42
    import random
    random.seed(rng)
    noise = [random.uniform(-1.0, 1.0) for _ in range(400)]
    rn = estimate_dual(noise, fs)
    _check("dual:noise_not_agree", rn.agreement is False)
    _check("dual:noise_review", rn.needs_review is True)
    _check("dual:noise_low_quality", rn.quality < 0.3, f"got {rn.quality}")
    print(f"    纯噪声: quality={rn.quality} agree={rn.agreement} review={rn.needs_review}")

    # 短窗口(5s):EEMD 呼吸不可靠应只比对心率,不误报 needs_review
    sig_short = synthesize_chest_signal(
        breath_hz=0.25, heart_hz=1.10, fs=fs, duration_s=5.0, noise=0.05, seed=7
    )
    rs = estimate_dual(sig_short, fs)
    _check("dual:shortwin_agree", rs.agreement is True, f"reason={rs.watch_reason}")
    _check("dual:shortwin_breath_dft", rs.breath_rate is not None and abs(rs.breath_rate - 15.0) <= 1.0, f"got {rs.breath_rate}")
    _check("dual:shortwin_no_review", rs.needs_review is False)
    print(f"    短窗口(5s): breath={rs.breath_rate} heart={rs.heart_rate} quality={rs.quality} agree={rs.agreement}")


def _run():
    print("=" * 60)
    print("双估计器投票测试 (DFT + EEMD)")
    print("=" * 60)
    _test_vote_unit()
    _test_estimate_dual_integration()
    print("=" * 60)
    if _FAILS:
        print(f"FAILED ({len(_FAILS)}): {', '.join(_FAILS)}")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(_run())
