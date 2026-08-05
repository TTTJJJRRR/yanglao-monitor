from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import BehaviorEvent, VitalSource
from ..schemas import BehaviorIn, BehaviorOut

router = APIRouter(prefix="/behaviors", tags=["behaviors"])


@router.post("", response_model=BehaviorOut)
def create_behavior(payload: BehaviorIn, db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = BehaviorEvent(**payload.model_dump(), source=VitalSource.real)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[BehaviorOut])
def list_behaviors(limit: int = 50, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(BehaviorEvent).order_by(BehaviorEvent.timestamp_ms.desc()).limit(limit).all()
