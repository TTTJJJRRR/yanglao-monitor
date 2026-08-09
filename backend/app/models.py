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
    mmfi = "mmfi"


class BehaviorAction(str, Enum):
    # 8 类安全动作（肆月 2026-08-09 锁定，老人安全视角）
    walking = "walking"              # 走动
    standing = "standing"            # 站立（从 normal_activity 拆出）
    sitting_still = "sitting_still"  # 静坐
    standing_up = "standing_up"      # 起身
    crouching = "crouching"          # 弯腰/蹲下/拾物（易误判为跌倒→必须单类）
    lying = "lying"                  # 卧床休息
    lying_floor = "lying_floor"      # 倒地不起（跌倒后状态=急救）
    falling = "falling"              # 跌倒（P0 红色警报）
    # 未知/其他兜底（低置信；融合层对之升级确认，不视为安全）
    normal_activity = "normal_activity"


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
    breath_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    heart_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    chest_displacement_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
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
