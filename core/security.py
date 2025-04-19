from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4
from models.user import User, TokenData
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from bson.objectid import ObjectId

from core.config import settings
from api.routes.auth.user_crud import get_user_by_email

ACCESS_TOKEN_EXPIRE_MINUTES = 600  # 10 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from a JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = await get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Check if the current user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_refresh_token(user_id: str) -> str:
    """Create a refresh token with longer expiration"""
    token_id = str(uuid4())
    expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    # Create token payload
    data = {
        "sub": str(user_id),
        "jti": token_id,
        "type": "refresh",
        "exp": expires,
    }

    # Generate JWT
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return token


async def store_refresh_token(user_id: str, token_id: str, expires: datetime) -> bool:
    """Store refresh token information in the database"""
    from core.db import db

    token_data = {
        "user_id": ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id,
        "token_id": token_id,
        "expires": expires,
        "created_at": datetime.utcnow(),
        "is_revoked": False,
    }

    result = await db.refresh_tokens.insert_one(token_data)
    return bool(result.inserted_id)


async def get_user_from_refresh_token(token: str) -> Optional[User]:
    """Validate a refresh token and return the associated user"""
    try:
        # Decode token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Check token type
        if payload.get("type") != "refresh":
            return None

        # Get user from token
        user_id = payload.get("sub")
        if not user_id:
            return None

        # Check if token is valid in database
        is_valid = await check_refresh_token_valid(token, payload.get("jti"))
        if not is_valid:
            return None

        # Get user
        user = await get_user_by_id(user_id)
        return user
    except JWTError:
        return None
