from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_active_user,
    get_password_hash,
)
from app.db.database import engine
from app.db.models import User
from app.models.user import Token, UserCreate, User as UserSchema
from app.schema.authentication import Login

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=UserSchema)
def signup(user: UserCreate):
    with Session(engine) as session:
        db_user = session.exec(
            select(User).where(User.username == user.username)
        ).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        db_user = session.exec(select(User).where(User.email == user.email)).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=str(user.email),
            hashed_password=hashed_password,
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Login) -> JSONResponse:
    user = User.authenticate_user(form_data.username, form_data.password)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid credentials"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})


@router.get("/users/me", response_model=UserSchema)
def read_users_me(current_user=Depends(get_current_active_user)) -> UserSchema:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return current_user
