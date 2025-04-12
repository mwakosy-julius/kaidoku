from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_serializer, Field as PydanticField
from typing import Annotated
from pydantic.functional_validators import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]



class UserBase(BaseModel):
    """Base user model with common fields"""

    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Model for creating a new user"""

    password: str


class User(UserBase):
    """User model with full user information"""

    id: Optional[PyObjectId] = PydanticField(alias="_id", default=None)
    is_active: bool = True
    created_at: datetime = datetime.now()

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

    @field_serializer("id")
    def serialize_id(self, id: PyObjectId) -> str:
        return str(id) if id else None

    def to_mongo(self):
        data = self.model_dump(by_alias=True, exclude={"id"})
        if self.id:
            data["_id"] = self.id
        return data

class UserInfo(UserBase):
    """User model with full user information"""

    id: Optional[PyObjectId] = PydanticField(alias="_id", default=None)
    password: str = ""
    is_active: bool = True
    created_at: datetime = datetime.now()

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

    @field_serializer("id")
    def serialize_id(self, id: PyObjectId) -> str:
        return str(id) if id else None

    def to_mongo(self):
        data = self.model_dump(by_alias=True, exclude={"id"})
        if self.id:
            data["_id"] = self.id
        return data

class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str

class TokenData(BaseModel):
    """Data stored in a JWT token"""

    email: Optional[str] = None


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str