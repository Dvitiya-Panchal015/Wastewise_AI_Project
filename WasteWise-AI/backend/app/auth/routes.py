from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone

from .database import get_db
from .models import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "change-this-to-a-long-random-secret-before-deployment"
ALGORITHM = "HS256"


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def create_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    if len(data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters"
        )

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=pwd_context.hash(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Registration successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user or not pwd_context.verify(
        data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_token(user.id)

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }