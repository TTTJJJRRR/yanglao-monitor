from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from .auth import decode_token
from .database import SessionLocal
from .models import Alert, BehaviorEvent, VitalRecord


async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        decode_token(token)
    except Exception:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        return


def save_and_build_message(db: Session, payload: dict, kind: str):
    if kind == "vital":
        record = VitalRecord(**payload)
        db.add(record)
        db.commit()
        db.refresh(record)
        return {"type": "vital", "data": {**payload, "id": record.id}}
    if kind == "behavior":
        record = BehaviorEvent(**payload)
        db.add(record)
        db.commit()
        db.refresh(record)
        return {"type": "behavior", "data": {**payload, "id": record.id}}
    alert = Alert(**payload)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return {"type": "alert", "data": {"id": alert.id, **payload}}
