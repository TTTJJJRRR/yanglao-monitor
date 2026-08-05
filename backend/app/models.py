from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class UserRole(str, Enum):
    family = "family"
    admin = "admin"
    elder = "elder"


class VitalSource(str, Enum):
    mock = "mock"
    real = "real"


class BehaviorAction(str, Enum):
    walking = "walking"          # 行走
    sitting = "sitting"           # 坐下
    lying = "lying"               # 躺下
    crouching = "crouching"       # 弯腰
    falling = "falling"           # 跌倒
    still = "still"               # 静止


class EmotionLabel(str, Enum):
    happy = "happy"
    sad = "sad"
    angry = "angry"
    anxious = "anxious"
    calm = "calm"
    surprised = "surprised"


class AlertLevel(str, Enum):
    red = "red"
    yellow = "yellow"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    hashed_pwd: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False)
    elder_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


class VitalRecord(Base):
    __tablename__ = "vital_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String(64), nullable=False)
    timestamp_ms: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    breath_rate: Mapped[float] = mapped_column(Float, nullable=False)
    heart_rate: Mapped[float] = mapped_column(Float, nullable=False)
    chest_displacement_mm: Mapped[float] = mapped_column(Float, nullable=False)
    motion_flag: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ahi_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[VitalSource] = mapped_column(SAEnum(VitalSource), nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BehaviorEvent(Base):
    __tablename__ = "behavior_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp_ms: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    action: Mapped[BehaviorAction] = mapped_column(SAEnum(BehaviorAction), nullable=False)
    emotion: Mapped[EmotionLabel] = mapped_column(SAEnum(EmotionLabel), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[VitalSource] = mapped_column(SAEnum(VitalSource), nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp_ms: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    level: Mapped[AlertLevel] = mapped_column(SAEnum(AlertLevel), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_handled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
