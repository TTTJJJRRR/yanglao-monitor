"""雷达 + 视觉 跌倒融合决策（M5 安全翻转）。

TI 官方没有现成的跌倒检测 lab，且视觉骨骼化不上云（隐私红线 R-P0-03），
因此跌倒判定必须在边缘侧做「雷达行为 + 视觉姿态」双模态融合。

本模块采用宁误报不漏报策略：
- 易混淆姿态或未知低置信输入，不再直接视为安全，而是升级为盯防。
- 跌倒判定保留红/黄警。
"""
from ..models import BehaviorAction


FALL_AMBIGUOUS = {
    BehaviorAction.crouching.value,
    BehaviorAction.lying.value,
    BehaviorAction.lying_floor.value,
}


def fuse(
    radar_action: str | None = None,
    radar_conf: float = 0.0,
    vision_fall_score: float = 0.0,
    vision_conf: float = 0.0,
) -> dict:
    """返回融合决策。

    返回字段：
        action: 融合后的行为枚举（BehaviorAction）
        confidence: 融合置信度
        is_fall: 是否判定为跌倒
        alert_level: 'red' | 'yellow' | None
        needs_review: 是否需要持续盯防
        watch_reason: 盯防原因
    """
    action = BehaviorAction.normal_activity.value
    confidence = 0.5
    is_fall = False
    alert_level = None
    needs_review = False
    watch_reason = None

    radar_fall = radar_action == BehaviorAction.falling.value and radar_conf >= 0.6
    vision_fall = vision_fall_score >= 0.6 and vision_conf >= 0.5

    if radar_fall and vision_fall:
        is_fall = True
        action = BehaviorAction.falling.value
        confidence = max(radar_conf, vision_conf)
        alert_level = "red"
    elif radar_fall and not vision_fall:
        is_fall = True
        action = BehaviorAction.falling.value
        confidence = radar_conf
        alert_level = "yellow"
    elif vision_fall and not radar_fall:
        is_fall = True
        action = BehaviorAction.falling.value
        confidence = vision_conf
        alert_level = "yellow"
    elif radar_action in FALL_AMBIGUOUS or radar_action == BehaviorAction.normal_activity.value:
        if radar_conf < 0.5:
            needs_review = True
            watch_reason = "low_conf_ambiguous_or_unknown"
        else:
            action = radar_action or BehaviorAction.normal_activity.value
            confidence = radar_conf
    elif radar_action in {BehaviorAction.walking.value, BehaviorAction.standing.value, BehaviorAction.sitting_still.value, BehaviorAction.standing_up.value} and radar_conf >= 0.5:
        action = radar_action
        confidence = radar_conf
    else:
        needs_review = True
        watch_reason = "fallback_watch"

    return {
        "action": action,
        "confidence": round(confidence, 2),
        "is_fall": is_fall,
        "alert_level": alert_level,
        "needs_review": needs_review,
        "watch_reason": watch_reason,
    }
