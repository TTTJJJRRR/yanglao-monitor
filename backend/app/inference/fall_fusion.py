"""雷达 + 视觉 跌倒融合决策（M3 评审命门）。

TI 官方没有现成的跌倒检测 lab，且视觉骨骼化不上云（隐私红线 R-P0-03），
因此跌倒判定必须在边缘侧做「雷达行为 + 视觉姿态」双模态融合。

接口（M0 骨架）：
    fuse(radar_action, radar_conf, vision_fall_score, vision_conf) -> dict
返回融合后的行为事件 + 是否触发跌倒报警。

算法 TODO（详见 deliverables/tech-plan/opensource-porting-guide）：
- 雷达侧：移植 radar-lab/patient_monitoring 的 6 类 CNN
  （行走 / 坐下 / 躺下 / 弯腰 / 跌倒 / 静止）。
- 视觉侧：移植 MediaPipe Pose 的跌倒线索
  （躯干-地面夹角、质心高度骤降 → fall_score）。
- 融合策略：双模态一致 → 高置信红警；单模态高置信 → 黄警待确认；
  冲突时以雷达为准（隐私安全优先，避免误报惊扰）。
"""
from ..models import BehaviorAction


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
    """
    action = BehaviorAction.still.value
    confidence = 0.5
    is_fall = False
    alert_level = None

    radar_fall = radar_action == BehaviorAction.falling.value and radar_conf >= 0.6
    vision_fall = vision_fall_score >= 0.6 and vision_conf >= 0.5

    if radar_fall and vision_fall:
        # 双模态一致 → 高置信跌倒（红警）
        is_fall = True
        action = BehaviorAction.falling.value
        confidence = max(radar_conf, vision_conf)
        alert_level = "red"
    elif radar_fall and not vision_fall:
        # 仅雷达判定 → 黄警（待家属 / 护工确认，避免误报）
        is_fall = True
        action = BehaviorAction.falling.value
        confidence = radar_conf
        alert_level = "yellow"
    elif vision_fall and not radar_fall:
        # 仅视觉判定 → 黄警（视觉不上云，仅作边缘辅助）
        is_fall = True
        action = BehaviorAction.falling.value
        confidence = vision_conf
        alert_level = "yellow"
    elif radar_action in {a.value for a in BehaviorAction} and radar_conf >= 0.5:
        action = radar_action
        confidence = radar_conf
    else:
        # 低置信雷达信号不可靠，回落为静止，避免大屏误显「跌倒」
        action = BehaviorAction.still.value
        confidence = 0.5

    return {
        "action": action,
        "confidence": round(confidence, 2),
        "is_fall": is_fall,
        "alert_level": alert_level,
    }
