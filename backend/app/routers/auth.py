from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import create_access_token, hash_password, verify_password
from app.db import get_session
from app.models import User
from app.schemas import LoginIn, RegisterIn, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == data.email)).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = User(email=data.email, password_hash=hash_password(data.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "email": user.email}


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(user.id)
    return TokenOut(access_token=token)
