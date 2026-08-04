import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import Base, engine, SessionLocal
from .mock import generate_alert, generate_behavior, generate_vital
from .models import Alert, BehaviorEvent, User, VitalRecord
from .routers.alerts import router as alerts_router
from .routers.auth import router as auth_router, seed_admin
from .routers.behaviors import router as behaviors_router
from .routers.vitals import router as vitals_router
from .ws import websocket_endpoint

settings = get_settings()
clients: set[WebSocket] = set()


async def mock_stream() -> None:
    while True:
        db = SessionLocal()
        try:
            vital = generate_vital()
            vital_record = VitalRecord(**vital)
            db.add(vital_record)
            db.commit()
            db.refresh(vital_record)
            await broadcast({"type": "vital", "data": {**vital, "id": vital_record.id}})

            if int(vital_record.timestamp_ms) % 5 == 0:
                behavior = generate_behavior()
                behavior_record = BehaviorEvent(**behavior)
                db.add(behavior_record)
                db.commit()
                db.refresh(behavior_record)
                await broadcast({"type": "behavior", "data": {**behavior, "id": behavior_record.id}})
                alert_payload = generate_alert(behavior["action"])
                if alert_payload:
                    alert = Alert(**alert_payload)
                    db.add(alert)
                    db.commit()
                    db.refresh(alert)
                    await broadcast({"type": "alert", "data": {"id": alert.id, **alert_payload}})
        finally:
            db.close()
        await asyncio.sleep(1)


async def broadcast(message: dict[str, Any]) -> None:
    stale: list[WebSocket] = []
    for client in clients:
        try:
            await client.send_json(message)
        except Exception:
            stale.append(client)
    for client in stale:
        clients.discard(client)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()
    task = asyncio.create_task(mock_stream())
    yield
    task.cancel()


app = FastAPI(title=settings.project_name, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(vitals_router, prefix=settings.api_prefix)
app.include_router(behaviors_router, prefix=settings.api_prefix)
app.include_router(alerts_router, prefix=settings.api_prefix)


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    clients.add(websocket)
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        clients.discard(websocket)


@app.post("/api/simulate/fall")
async def simulate_fall():
    db = SessionLocal()
    try:
        payload = {"timestamp_ms": int(asyncio.get_running_loop().time() * 1000), "level": "red", "type": "fall", "message": "检测到跌倒，请立即查看", "is_handled": False}
        alert = Alert(**payload)
        db.add(alert)
        db.commit()
        db.refresh(alert)
        await broadcast({"type": "alert", "data": {"id": alert.id, **payload}})
        return {"ok": True, "alert": {"id": alert.id, **payload}}
    finally:
        db.close()
