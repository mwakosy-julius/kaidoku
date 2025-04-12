from models.user import User, UserCreate, UserInfo
from datetime import datetime
from typing import Optional
from core.db import user_collection
from models.user import PyObjectId
from passlib.context import CryptContext

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
    return UserInfo(**created_user)


async def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by username"""
    user_data = await user_collection.find_one({"username": username})
    if user_data:
        return UserInfo(**user_data)
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
