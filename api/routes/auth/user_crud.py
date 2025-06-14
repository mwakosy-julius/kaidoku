from models.user import User, UserCreate, UserInfo
from datetime import datetime
from typing import Optional
from core.config import settings
from core.db import user_collection
from models.user import PyObjectId
from passlib.context import CryptContext
from core.db import db
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


async def create_user(user: UserCreate) -> User:
    """Create a new user in the database"""
    user_data = user.model_dump(by_alias=True, exclude=["id"])
    user_data["password"] = get_password_hash(user_data["password"])

    user_data["created_at"] = datetime.now()
    result = await user_collection.insert_one(user_data)

    created_user = await user_collection.find_one({"_id": result.inserted_id})
    if created_user:
        return User(
            **{
                k: v
                for k, v in created_user.items()
                if k != "_id" or isinstance(k, str)
            }
        )
    raise ValueError("Failed to create user")
    # return UserInfo(**created_user)


async def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by username"""
    user_data = await user_collection.find_one({"username": username})
    if user_data:
        return User(
            **{k: v for k, v in user_data.items() if k != "_id" or isinstance(k, str)}
        )
    return None


async def get_user_by_email(email: str) -> Optional[User]:
    """Get a user by email"""
    user_data = await user_collection.find_one({"email": email})
    if user_data:
        return UserInfo(**user_data)
    return None


async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get a user by ID"""
    user_data = await user_collection.find_one({"_id": PyObjectId(user_id)})
    if user_data:
        return UserInfo(**user_data)
    return None


async def add_refresh_token(user_id: str, token_id: str, expires: datetime) -> bool:
    """Add a refresh token to the database"""
    result = await db.refresh_tokens.insert_one(
        {
            "user_id": user_id,
            "token_id": token_id,
            "expires": expires,
            "created_at": datetime.utcnow(),
            "is_revoked": False,
        }
    )
    return bool(result.inserted_id)


async def invalidate_refresh_token(token: str) -> bool:
    """Invalidate a refresh token"""
    try:
        # Decode token to get ID
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_id = payload.get("jti")

        # Mark token as revoked
        result = await db.refresh_tokens.update_one(
            {"token_id": token_id}, {"$set": {"is_revoked": True}}
        )
        return result.modified_count > 0
    except Exception:
        return False


async def check_refresh_token_valid(token: str, token_id: str) -> bool:
    """Check if a refresh token is valid"""
    token_doc = await db.refresh_tokens.find_one({"token_id": token_id})
    if not token_doc:
        return False

    return (
        not token_doc.get("is_revoked", False)
        and token_doc.get("expires") > datetime.utcnow()
    )
