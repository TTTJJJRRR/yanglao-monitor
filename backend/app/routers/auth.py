from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import create_access_token, get_current_user, hash_password, verify_password
from ..database import get_db
from ..models import User, UserRole
from ..schemas import LoginBody, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_pwd):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = create_access_token(user.username, user.role.value)
    return TokenResponse(access_token=token, role=user.role.value)


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user


def seed_admin(db: Session) -> None:
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(username="admin", hashed_pwd=hash_password("admin123"), role=UserRole.admin, elder_id=None))
        db.commit()
