from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4
from models.user import User, UserInDB, TokenData, RefreshToken, UserResponse
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from bson.objectid import ObjectId

from core.config import settings
from api.routes.auth.user_crud import get_user_by_email

# Token expiration settings
ACCESS_TOKEN_EXPIRE_MINUTES = 600  # 10 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security context and OAuth2 scheme
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

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


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
        "iat": datetime.utcnow(),
    }

    # Generate JWT
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


async def store_refresh_token(user_id: str, token_id: str, expires: datetime) -> bool:
    """Store refresh token information in the database"""
    from core.db import db

    try:
        # Convert user_id to ObjectId if it's a string
        user_object_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id

        # Create refresh token document
        refresh_token = RefreshToken(
            user_id=user_object_id,
            token_id=token_id,
            expires=expires,
            created_at=datetime.utcnow(),
            is_revoked=False
        )

        # Insert into database
        result = await db.refresh_tokens.insert_one(refresh_token.to_mongo())
        return bool(result.inserted_id)
    except Exception as e:
        # Log the error in production
        print(f"Error storing refresh token: {e}")
        return False


async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
    """Get user by ID from database"""
    from core.db import db

    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(user_id)

        # Query database
        user_doc = await db.users.find_one({"_id": object_id})

        if user_doc:
            # Convert MongoDB document to UserInDB model
            return UserInDB(**user_doc)
        return None
    except Exception as e:
        print(f"Error getting user by ID: {e}")
        return None


async def check_refresh_token_valid(token: str, jti: str) -> bool:
    """Check if refresh token is valid and not revoked"""
    from core.db import db

    try:
        # Query database for token
        token_doc = await db.refresh_tokens.find_one({
            "token_id": jti,
            "is_revoked": False,
            "expires": {"$gt": datetime.utcnow()}
        })

        return token_doc is not None
    except Exception as e:
        print(f"Error checking refresh token validity: {e}")
        return False


async def invalidate_refresh_token(token: str) -> bool:
    """Mark refresh token as revoked"""
    from core.db import db

    try:
        # Decode token to get JTI
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        jti = payload.get("jti")

        if not jti:
            return False

        # Update token to mark as revoked
        result = await db.refresh_tokens.update_one(
            {"token_id": jti},
            {"$set": {"is_revoked": True, "revoked_at": datetime.utcnow()}}
        )

        return result.modified_count > 0
    except JWTError:
        return False
    except Exception as e:
        print(f"Error invalidating refresh token: {e}")
        return False


async def cleanup_expired_tokens():
    """Remove expired refresh tokens from database"""
    from core.db import db

    try:
        # Delete expired tokens
        result = await db.refresh_tokens.delete_many({
            "expires": {"$lt": datetime.utcnow()}
        })
        return result.deleted_count
    except Exception as e:
        print(f"Error cleaning up expired tokens: {e}")
        return 0


async def revoke_all_user_tokens(user_id: str) -> bool:
    """Revoke all refresh tokens for a specific user"""
    from core.db import db

    try:
        user_object_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id

        result = await db.refresh_tokens.update_many(
            {"user_id": user_object_id, "is_revoked": False},
            {"$set": {"is_revoked": True, "revoked_at": datetime.utcnow()}}
        )

        return result.modified_count > 0
    except Exception as e:
        print(f"Error revoking user tokens: {e}")
        return False


async def get_user_from_refresh_token(token: str) -> Optional[UserResponse]:
    """Validate a refresh token and return the associated user"""
    try:
        # Decode token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Check token type
        if payload.get("type") != "refresh":
            return None

        # Get user ID and JTI from token
        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not user_id or not jti:
            return None

        # Check if token is valid in database
        is_valid = await check_refresh_token_valid(token, jti)
        if not is_valid:
            return None

        # Get user from database
        user_in_db = await get_user_by_id(user_id)
        if not user_in_db:
            return None

        # Return User model (without password)
        return UserResponse(
            _id=user_in_db.id,
            username=user_in_db.username,
            email=user_in_db.email,
            is_active=user_in_db.is_active,
            created_at=user_in_db.created_at
        )

    except JWTError:
        return None
    except Exception as e:
        print(f"Error getting user from refresh token: {e}")
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """Get the current user from a JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Check token type
        if payload.get("type") != "access":
            raise credentials_exception

        # Extract email from token
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception

        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    # Get user from database
    user = await get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception

    # Return User model (without password)
    return UserResponse(
        _id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at
    )


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Check if the current user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def verify_token_format(token: str) -> bool:
    """Verify that a token has the correct JWT format"""
    try:
        jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False}  # Don't verify expiration for format check
        )
        return True
    except JWTError:
        return False


async def rotate_refresh_token(old_token: str, user_id: str) -> Optional[str]:
    """Rotate refresh token (invalidate old one and create new one)"""
    try:
        # Invalidate old token
        await invalidate_refresh_token(old_token)

        # Create new refresh token
        new_token = create_refresh_token(user_id)

        # Decode new token to get JTI and expiration
        payload = jwt.decode(
            new_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti or not exp:
            return None

        # Store new token in database
        expires = datetime.fromtimestamp(exp)
        success = await store_refresh_token(user_id, jti, expires)

        if success:
            return new_token
        return None

    except Exception as e:
        print(f"Error rotating refresh token: {e}")
        return None
