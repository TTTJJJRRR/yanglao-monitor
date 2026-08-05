from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import VitalRecord, VitalSource
from ..schemas import VitalIn, VitalOut

router = APIRouter(prefix="/vitals", tags=["vitals"])


@router.post("", response_model=VitalOut)
def create_vital(payload: VitalIn, db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = VitalRecord(**payload.model_dump(), source=VitalSource.real)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[VitalOut])
def list_vitals(limit: int = 50, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(VitalRecord).order_by(VitalRecord.timestamp_ms.desc()).limit(limit).all()
