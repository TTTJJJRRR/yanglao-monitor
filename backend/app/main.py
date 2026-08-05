import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .bus import clients, broadcast
from .config import get_settings
from .database import Base, engine, SessionLocal
from .mock import generate_alert, generate_behavior, generate_vital
from .models import Alert, BehaviorEvent, User, VitalRecord
from .routers.alerts import router as alerts_router
from .routers.auth import router as auth_router, seed_admin
from .routers.behaviors import router as behaviors_router
from .routers.edge import router as edge_router
from .routers.vitals import router as vitals_router
from .ws import websocket_endpoint
from .data_source import get_source, set_source, next_mmfi_messages, next_real_vital, available_sources

settings = get_settings()


async def mock_stream() -> None:
    """后台推送任务：根据全局数据源选择 mock 或 mmfi。

    - mock：复用现有生成器，写库 + 广播（原逻辑）。
    - mmfi：读取 data/mmfi-sample/radar_sample.jsonl，仅广播不落库
      （样例生命体征为 null，不满足 VitalRecord 非空约束；样例仅含雷达帧，
      无行为/报警真值）。行为/跌倒演示仍可走前端手动 POST /api/simulate/fall。
    """
    while True:
        if get_source() == "mmfi":
            for msg in next_mmfi_messages():
                await broadcast(msg)
            await asyncio.sleep(1)
            continue

        if get_source() == "real":
            vital = next_real_vital()
            if vital is not None:
                db = SessionLocal()
                try:
                    record = VitalRecord(**vital)
                    db.add(record)
                    db.commit()
                    db.refresh(record)
                    await broadcast({"type": "vital", "data": {**vital, "id": record.id}})
                finally:
                    db.close()
            await asyncio.sleep(1)
            continue

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
app.include_router(edge_router, prefix=settings.api_prefix)


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


class DataSourceSwitch(BaseModel):
    source: str


@app.get("/api/data-source")
async def get_data_source():
    return {"source": get_source(), "options": available_sources()}


@app.post("/api/data-source")
async def switch_data_source(body: DataSourceSwitch):
    if not set_source(body.source):
        raise HTTPException(status_code=400, detail="invalid source, must be one of " + str(available_sources()))
    return {"source": get_source(), "options": available_sources()}
