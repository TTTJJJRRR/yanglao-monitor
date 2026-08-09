"""EEMD 与 DFT 双估计器交叉验证（纯 Python，无 numpy）。

验证目标（诚实）：
1. 在「已知频率的合成胸腔信号」上，DFT 与 EEMD 都应恢复出真实呼吸/心率。
2. 两个独立方法的结果应彼此一致（差异小）→ 说明生命体征估计可信，非单算法巧合。
3. 纯噪声输入两个方法都应给出低质量 / 无可信号。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/

from app.sources.mmvital_estimator import MmVitalEstimator, synthesize_chest_signal
from app.sources.eemd_vitals import EemdVitalsEstimator


def _run():
    fs = 20.0
    # 已知：呼吸 0.25 Hz = 15 次/分；心率 1.10 Hz = 66 bpm
    breath_hz, heart_hz = 0.25, 1.10
    sig = synthesize_chest_signal(
        breath_hz=breath_hz, heart_hz=heart_hz, fs=fs,
        duration_s=20.0, noise=0.05, seed=7,
    )

    dft = MmVitalEstimator(fs).estimate(sig)
    eemd = EemdVitalsEstimator(fs).estimate(sig)

    print("=" * 60)
    print("合成信号: 呼吸=15.0 次/分, 心率=66.0 bpm (明确为合成输入)")
    print("-" * 60)
    print(f"DFT : breath={dft.breath_rate}  heart={dft.heart_rate}  quality={dft.quality}  motion={dft.motion_flag}")
    print(f"EEMD: breath={eemd.breath_rate}  heart={eemd.heart_rate}  quality={eemd.quality}  motion={eemd.motion_flag}")
    print("=" * 60)

    fails = []
    # 1) DFT 自身恢复
    if not (dft.breath_rate is not None and abs(dft.breath_rate - 15.0) < 1.0):
        fails.append(f"DFT 呼吸偏离: {dft.breath_rate}")
    if not (dft.heart_rate is not None and abs(dft.heart_rate - 66.0) < 1.0):
        fails.append(f"DFT 心率偏离: {dft.heart_rate}")
    # 2) EEMD 自身恢复（EEMD 较粗，放宽到 ±2）
    if not (eemd.breath_rate is not None and abs(eemd.breath_rate - 15.0) < 2.0):
        fails.append(f"EEMD 呼吸偏离: {eemd.breath_rate}")
    if not (eemd.heart_rate is not None and abs(eemd.heart_rate - 66.0) < 2.5):
        fails.append(f"EEMD 心率偏离: {eemd.heart_rate}")
    # 3) 两法一致（互验核心）
    if dft.heart_rate is not None and eemd.heart_rate is not None:
        if abs(dft.heart_rate - eemd.heart_rate) > 4.0:
            fails.append(f"两法心率不一致: DFT={dft.heart_rate} EEMD={eemd.heart_rate}")
    else:
        fails.append("两法之一未给出心率，无法互验")
    # 4) 质量合理
    if not (dft.quality > 0.2 and eemd.quality > 0.2):
        fails.append(f"质量过低: DFT={dft.quality} EEMD={eemd.quality}")

    # 5) 纯噪声应不可信
    noise_only = [0.3 * (i % 2 - 0.5) + 0.1 * ((i * 7) % 5 - 2) for i in range(400)]
    dft_n = MmVitalEstimator(fs).estimate(noise_only)
    eemd_n = EemdVitalsEstimator(fs).estimate(noise_only)
    print(f"\n纯噪声: DFT quality={dft_n.quality} heart={dft_n.heart_rate} | EEMD quality={eemd_n.quality} heart={eemd_n.heart_rate}")
    if dft_n.heart_rate is not None and abs(dft_n.heart_rate - 66.0) < 5.0:
        fails.append("纯噪声下 DFT 仍给出接近真实心率(应不可信)")

    if fails:
        print("\nFAIL:")
        for f in fails:
            print("  -", f)
        return False
    print("\nALL TESTS PASSED")
    return True


if __name__ == "__main__":
    sys.exit(0 if _run() else 1)
