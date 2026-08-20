"""边缘节点接入路由（M0 骨架，无硬件可联调）。

边缘侧（树莓派 / Jetson）运行 edge/vision_node.py 与雷达解析进程，
通过这两个端点把「雷达行为」和「视觉姿态」推给后端做融合决策：

    POST /api/edge/behavior   { device_id, action, confidence }
    POST /api/edge/pose       { device_id, fall_score, confidence }

后端用 inference/fall_fusion.fuse 融合，落库行为事件 + 触发报警，并广播。
"""
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..bus import broadcast
from ..database import SessionLocal
from ..inference.fall_fusion import fuse
from ..inference.behavior_classifier import (
    RadarFrame,
    get_classifier,
    ModelNotLoadedError,
    StubBehaviorClassifier,
)
from ..models import BehaviorAction, EmotionLabel
from ..ws import save_and_build_message

router = APIRouter(tags=["edge"])


class RadarBehavior(BaseModel):
    device_id: str = "RADAR_01"
    action: str
    confidence: float = 0.0


class VisionPose(BaseModel):
    device_id: str = "CAM_01"
    fall_score: float = 0.0
    confidence: float = 0.0
    is_fall: bool | None = None
    alert_level: str | None = None
    watch: bool | None = None
    needs_review: bool | None = None
    watch_reason: str | None = None


# 最近一次双模态状态（单设备演示用；M2 按 device_id 分桶）
_state = {
    "radar_action": None,
    "radar_conf": 0.0,
    "vision_fall_score": 0.0,
    "vision_conf": 0.0,
    "vision_watch": False,
    "vision_alert_level": None,
}


def _now_ms() -> int:
    return int(time.time() * 1000)


async def _sync_and_decide() -> dict:
    decision = fuse(
        radar_action=_state["radar_action"],
        radar_conf=_state["radar_conf"],
        vision_fall_score=_state["vision_fall_score"],
        vision_conf=_state["vision_conf"],
    )
    db = SessionLocal()
    try:
        behavior_payload = {
            "timestamp_ms": _now_ms(),
            "action": decision["action"],
            "emotion": EmotionLabel.calm.value,
            "confidence": decision["confidence"],
            "source": "real",
        }
        behavior_msg = save_and_build_message(db, behavior_payload, "behavior")
        await broadcast(behavior_msg)

        await broadcast({
            "type": "radar_status",
            "data": {
                "action": _state["radar_action"],
                "confidence": round(_state["radar_conf"], 3),
                "model_loaded": not isinstance(get_classifier(), StubBehaviorClassifier),
            },
        })
        await broadcast({
            "type": "pose",
            "data": {
                "fall_score": round(_state["vision_fall_score"], 3),
                "confidence": round(_state["vision_conf"], 3),
                "is_fall": bool(decision["is_fall"]),
                "alert_level": decision["alert_level"],
                "watch": bool(_state["vision_watch"]),
            },
        })

        if decision["alert_level"]:
            alert_payload = {
                "timestamp_ms": _now_ms(),
                "level": decision["alert_level"],
                "type": "fall",
                "message": "融合判定跌倒，请立即查看"
                if decision["alert_level"] == "red"
                else "疑似跌倒，请确认老人状态",
                "is_handled": False,
            }
            alert_msg = save_and_build_message(db, alert_payload, "alert")
            await broadcast(alert_msg)
        return decision
    finally:
        db.close()


@router.post("/edge/behavior")
async def post_radar_behavior(body: RadarBehavior):
    _state["radar_action"] = body.action
    _state["radar_conf"] = body.confidence
    decision = await _sync_and_decide()
    return {"ok": True, "decision": decision}


class RadarFrameIn(BaseModel):
    device_id: str = "RADAR_01"
    timestamp_ms: int = 0
    signature: list | None = None


@router.post("/edge/radar-frame")
async def post_radar_frame(body: RadarFrameIn):
    classifier = get_classifier()
    frame = RadarFrame(
        device_id=body.device_id,
        timestamp_ms=body.timestamp_ms or _now_ms(),
        signature=body.signature,
    )
    try:
        pred = classifier.classify(frame)
    except ModelNotLoadedError as e:
        raise HTTPException(status_code=503, detail=str(e))
    _state["radar_action"] = pred.action.value
    _state["radar_conf"] = pred.confidence
    decision = await _sync_and_decide()
    return {"ok": True, "decision": decision}


@router.post("/edge/pose")
async def post_vision_pose(body: VisionPose):
    _state["vision_fall_score"] = body.fall_score
    _state["vision_conf"] = body.confidence
    _state["vision_watch"] = bool(body.watch or body.needs_review)
    _state["vision_alert_level"] = body.alert_level
    if body.is_fall is True:
        _state["vision_fall_score"] = max(_state["vision_fall_score"], 0.8)
    decision = await _sync_and_decide()
    return {"ok": True, "decision": decision}
