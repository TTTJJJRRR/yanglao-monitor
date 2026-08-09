"""DFT + EEMD 双估计器投票（Wave 0 融合卡位）。

两个**独立**生命体征估计器 —— DFT 周期图(`mmvital_estimator`)与 EEMD 经验模态
分解(`eemd_vitals`) —— 对同一段相位信号分别估计呼吸/心率。两者结论一致 =>
提升可信度(high quality, 取均值);不一致 => 降置信并标记 `needs_review`,交给融合层
/ 家属端盯防,**绝不静默当成安全**(延续 M5 融合安全翻转的"宁误报不漏报"原则)。

设计要点:
- 纯算法、无训练数据依赖 —— 等 M4 真实多类数据到位后,可再升级为加权 / 模型投票。
- `vote()` 是纯函数,直接吃两个 `VitalEstimate`,便于确定性单测覆盖 一致/分歧/缺检 三态。
- `estimate_dual()` 是集成入口:跑两个估计器后调用 `vote()`。
- 信任门槛 `MIN_QUALITY`:任一估计器 quality 过低(如纯噪声)直接判为不可交叉验证,
  不会因"两法都瞎猜且碰巧接近"而误报一致。
"""
from __future__ import annotations

from dataclasses import dataclass

from .mmvital_estimator import VitalEstimate, estimate_vitals
from .eemd_vitals import estimate_eemd


# ---- 投票阈值（可随真实数据校准）------------------------------------------------
BREATH_TOL = 3.0          # 次/分：两法呼吸率偏差在此内算一致
HEART_TOL = 5.0           # bpm：两法心率偏差在此内算一致
MIN_QUALITY = 0.30        # 任一估计器质量低于此值,视为不可信、不参与"一致"判定
MIN_WINDOW_S = 12.0       # 秒：短于此窗口 EEMD 无法稳定分离呼吸 IMF,其呼吸不可靠
QUALITY_AGREE_BOOST = 0.10    # 一致时 quality 加成(上限见 _cap)
QUALITY_DISAGREE_PENALTY = 0.5  # 不一致 / 缺检时 quality 乘子
_QUALITY_CAP = 0.99


@dataclass
class DualVitalEstimate:
    breath_rate: float | None
    heart_rate: float | None
    motion_flag: bool
    quality: float
    agreement: bool                 # 两法是否一致(且均过质量门槛)
    dft: VitalEstimate              # 保留两路原始估计,便于溯源/调试
    eemd: VitalEstimate
    needs_review: bool = False      # 不一致或缺检 → 转盯防
    watch_reason: str | None = None


def _cap(q: float) -> float:
    return round(min(_QUALITY_CAP, max(0.0, q)), 3)


def _rates_agree(dft: VitalEstimate, eemd: VitalEstimate) -> bool:
    """两法频率结论是否一致(不含质量门槛,质量在 vote() 单独判定)。

    心率必须双方可比对;motion_flag 必须一致。呼吸率仅在 EEMD 给出可信呼吸
    (非 None,即非短窗口降级)时才参与比对 —— 短窗口下 EEMD 呼吸不可靠,只比对心率。
    """
    if dft.heart_rate is None or eemd.heart_rate is None:
        return False
    if dft.motion_flag != eemd.motion_flag:
        return False
    if dft.breath_rate is not None and eemd.breath_rate is not None:
        if abs(dft.breath_rate - eemd.breath_rate) > BREATH_TOL:
            return False
    if abs(dft.heart_rate - eemd.heart_rate) > HEART_TOL:
        return False
    return True


def vote(dft: VitalEstimate, eemd: VitalEstimate) -> DualVitalEstimate:
    """对两路估计做投票,产出最终生命体征与可信度标记。纯函数。

    四态:① DFT 缺检 → 单源不可交叉验证;② 任一质量过低 → 不可信;
    ③ 两法一致 → 提升可信(取均值);④ 两法分歧 → 降可信 + 盯防。
    后三种(非一致)均置 needs_review=True,绝不静默当成安全。
    """
    # ① 主估计器(DFT)都估不出生命体征 → 直接低可信、转盯防(单源不可交叉验证)
    if dft.breath_rate is None or dft.heart_rate is None:
        return DualVitalEstimate(
            breath_rate=eemd.breath_rate,
            heart_rate=eemd.heart_rate,
            motion_flag=dft.motion_flag or eemd.motion_flag,
            quality=_cap(min(dft.quality, eemd.quality) * QUALITY_DISAGREE_PENALTY),
            agreement=False,
            dft=dft,
            eemd=eemd,
            needs_review=True,
            watch_reason="DFT未检出生命体征,EEMD单源不可交叉验证",
        )

    # ② 质量门槛:任一估计器质量过低 → 不可信,转盯防(避免两法瞎猜碰巧接近误报一致)
    if dft.quality < MIN_QUALITY or eemd.quality < MIN_QUALITY:
        low = "/".join(
            n for n, q in (("DFT", dft.quality), ("EEMD", eemd.quality)) if q < MIN_QUALITY
        )
        return DualVitalEstimate(
            breath_rate=dft.breath_rate,
            heart_rate=dft.heart_rate,
            motion_flag=dft.motion_flag or eemd.motion_flag,
            quality=_cap(min(dft.quality, eemd.quality) * QUALITY_DISAGREE_PENALTY),
            agreement=False,
            dft=dft,
            eemd=eemd,
            needs_review=True,
            watch_reason=f"{low}质量过低,生命体征不可交叉验证",
        )

    # ③ 两法一致 → 提升可信(取均值;EEMD 呼吸不可靠时呼吸以 DFT 为准)
    if _rates_agree(dft, eemd):
        if eemd.breath_rate is None:
            breath = dft.breath_rate  # 短窗口:EEMD 呼吸不可靠,用 DFT
        else:
            breath = round((dft.breath_rate + eemd.breath_rate) / 2.0, 1)
        heart = round((dft.heart_rate + eemd.heart_rate) / 2.0, 1)
        quality = _cap(max(dft.quality, eemd.quality) + QUALITY_AGREE_BOOST)
        return DualVitalEstimate(
            breath_rate=breath,
            heart_rate=heart,
            motion_flag=dft.motion_flag,
            quality=quality,
            agreement=True,
            dft=dft,
            eemd=eemd,
        )

    # ④ 两法分歧 → 降可信 + 盯防(宁误报不漏报)
    quality = _cap(min(dft.quality, eemd.quality) * QUALITY_DISAGREE_PENALTY)
    b_e = eemd.breath_rate if eemd.breath_rate is not None else "n/a"
    return DualVitalEstimate(
        breath_rate=dft.breath_rate,
        heart_rate=dft.heart_rate,
        motion_flag=dft.motion_flag or eemd.motion_flag,
        quality=quality,
        agreement=False,
        dft=dft,
        eemd=eemd,
        needs_review=True,
        watch_reason=(
            f"DFT与EEMD生命体征分歧(呼吸 {dft.breath_rate} vs {b_e}, "
            f"心率 {dft.heart_rate} vs {eemd.heart_rate})"
        ),
    )


def estimate_dual(phase_signal: list[float], fs: float) -> DualVitalEstimate:
    """集成入口:同时跑 DFT 与 EEMD,再投票。返回带可信度标记的 DualVitalEstimate。

    窗口长度感知:呼吸周期(~4s)远长于心率,短窗口(< MIN_WINDOW_S)下 EEMD 无法稳定
    分离呼吸 IMF,其 breath_rate 不可靠。此时仅用 EEMD 的**心率**(短窗口仍可分辨)做
    交叉验证,呼吸率以 DFT 为准,避免"两法呼吸分歧"的误报盯防。
    """
    dft = estimate_vitals(phase_signal, fs)
    eemd = estimate_eemd(phase_signal, fs)
    if len(phase_signal) / fs < MIN_WINDOW_S and eemd.breath_rate is not None:
        # 短窗口:EEMD 呼吸不可靠 → 不参与呼吸交叉验证(心率仍可用)
        eemd = VitalEstimate(
            breath_rate=None,
            heart_rate=eemd.heart_rate,
            motion_flag=eemd.motion_flag,
            quality=eemd.quality,
        )
    return vote(dft, eemd)
