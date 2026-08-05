from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import AlertLevel, BehaviorAction, EmotionLabel, VitalSource


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    elder_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class VitalIn(BaseModel):
    timestamp_ms: int
    device_id: str
    breath_rate: float | None = Field(default=None, ge=0)
    heart_rate: float | None = Field(default=None, ge=0)
    chest_displacement_mm: float | None = Field(default=None, ge=0)
    motion_flag: bool
    ahi_index: float | None = None


class VitalOut(VitalIn):
    id: int
    source: VitalSource = VitalSource.mock

    model_config = ConfigDict(from_attributes=True)


class BehaviorIn(BaseModel):
    timestamp_ms: int
    action: BehaviorAction
    emotion: EmotionLabel
    confidence: float = Field(ge=0, le=1)


class BehaviorOut(BehaviorIn):
    id: int
    source: VitalSource = VitalSource.mock

    model_config = ConfigDict(from_attributes=True)


class AlertOut(BaseModel):
    id: int
    timestamp_ms: int
    level: AlertLevel
    type: str
    message: str
    is_handled: bool = False

    model_config = ConfigDict(from_attributes=True)


class LoginBody(BaseModel):
    username: str
    password: str


class SimulateFallResponse(BaseModel):
    ok: bool
    alert: AlertOut
