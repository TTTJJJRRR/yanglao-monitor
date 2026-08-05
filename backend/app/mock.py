import random
import time

from .models import BehaviorAction, EmotionLabel


def now_ms() -> int:
    return int(time.time() * 1000)


def generate_vital() -> dict:
    return {
        "timestamp_ms": now_ms(),
        "device_id": "RADAR_01",
        "breath_rate": round(random.uniform(12, 20), 1),
        "heart_rate": round(random.uniform(60, 100), 1),
        "chest_displacement_mm": round(random.uniform(1, 8), 1),
        "motion_flag": random.choice([True, False]),
        "ahi_index": None,
        "source": "mock",
    }


def generate_behavior() -> dict:
    return {
        "timestamp_ms": now_ms(),
        "action": random.choice(list(BehaviorAction)).value,
        "emotion": random.choice(list(EmotionLabel)).value,
        "confidence": round(random.uniform(0.7, 0.99), 2),
        "source": "mock",
    }


def generate_alert(action: str | None = None) -> dict | None:
    if action == "falling" or random.random() < 0.1:
        level = "red" if action == "falling" else "yellow"
        alert_type = "fall" if action == "falling" else "anomaly"
        message = "检测到跌倒，请立即查看" if action == "falling" else "检测到异常状态，请关注老人情况"
        return {"timestamp_ms": now_ms(), "level": level, "type": alert_type, "message": message, "is_handled": False}
    return None
