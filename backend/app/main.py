import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .bus import broadcast, clients, register_client, unregister_client
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
from .data_source import AVAILABLE, available_sources, get_source, next_mmfi_messages, next_real_vital, next_replay_messages, set_source
from .monitoring import DeviceMonitor

settings = get_settings()
monitor = DeviceMonitor(timeout_s=5.0)


async def mock_stream() -> None:
    """后台推送任务：根据全局数据源选择 mock 或 mmfi。

    - mock：复用现有生成器，写库 + 广播（原逻辑）。
    - mmfi：读取 data/mmfi-sample/radar_sample.jsonl，仅广播不落库
      （样例生命体征为 null，不满足 VitalRecord 非空约束；样例仅含雷达帧，
      无行为/报警真值）。行为/跌倒演示仍可走前端手动 POST /api/simulate/fall。
    - replay：回放同学采集的 jsonl（成品体征 + 动作标签），仅广播不落库
      （诚实标注：非实时检测，仅供验证前端管道）。
    """
    while True:
        if get_source() == "replay":
            for msg in next_replay_messages():
                await broadcast(msg, source="replay")
            # 以「now」刷新心跳，避免把回放的旧时间戳误判为设备离线
            monitor.touch("replay", int(time.time() * 1000))
            await monitor.publish_checks()
            await asyncio.sleep(1)
            continue

        if get_source() == "mmfi":
            for msg in next_mmfi_messages():
                await broadcast(msg, source="mmfi")
                monitor.touch("mmfi", msg["data"].get("timestamp_ms"))
            await monitor.publish_checks()
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
                    await broadcast({"type": "vital", "data": {**vital, "id": record.id}}, source="real")
                    monitor.touch("real", vital.get("timestamp_ms"))
                finally:
                    db.close()
            await monitor.publish_checks()
            await asyncio.sleep(1)
            continue

        db = SessionLocal()
        try:
            vital = generate_vital()
            vital_record = VitalRecord(**vital)
            db.add(vital_record)
            db.commit()
            db.refresh(vital_record)
            await broadcast({"type": "vital", "data": {**vital, "id": vital_record.id}}, source="mock")
            monitor.touch("mock", vital.get("timestamp_ms"))

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
        await monitor.publish_checks()
        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()

    # 雷达行为 CNN 即插即用注册：
    # 权重(weights.pt)存在且环境有 numpy/torch 时注册真实模型，
    # 否则保持空挡 Stub（/api/edge/radar-frame 返回 503，不伪造）。
    # Cursor 训练完把 weights.pt 放入 backend/app/inference/mmwave_cnn/ 即自动接入，零改代码。
    try:
        from .inference.behavior_classifier import register_classifier
        from .inference.mmwave_cnn.classifier import MmWaveBehaviorCNN

        register_classifier(MmWaveBehaviorCNN())
        print("[启动] 雷达行为 CNN 已接入（真实权重已加载）")
    except FileNotFoundError:
        print("[启动] 雷达行为 CNN 未接入：weights.pt 缺失，保持空挡接口（Cursor 训练后放入即生效）")
    except Exception as e:  # noqa: BLE001 - 后端无 numpy/torch 属正常，权重由 Cursor 环境加载
        print(f"[启动] 雷达行为 CNN 未接入：{type(e).__name__}（后端未装 numpy/torch，属正常；权重由 Cursor 环境加载）")

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


async def _accept_stream(websocket: WebSocket, requested_source: str | None = None) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    if requested_source is not None and requested_source not in AVAILABLE:
        await websocket.close(code=1008, reason="invalid source")
        return
    register_client(websocket, requested_source)
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        unregister_client(websocket)


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await _accept_stream(websocket, websocket.query_params.get("source"))


@app.websocket("/ws/stream")
async def ws_stream(websocket: WebSocket):
    await _accept_stream(websocket, websocket.query_params.get("source"))


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
