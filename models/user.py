from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_serializer, Field
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
    """User model for API responses (no password)"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

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

class UserResponse(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

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

class UserInDB(User):
    """User model with password for database operations"""
    password: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str

class TokenData(BaseModel):
    """Data stored in a JWT token"""
    email: Optional[str] = None
    user_id: Optional[str] = None  # Added for better token validation

class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str

class RefreshToken(BaseModel):
    """Model for refresh token storage in database"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    token_id: str  # JWT ID (jti)
    expires: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    is_revoked: bool = False

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

class UserProfile(User):
    """Extended user profile with additional fields"""
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None
    # Add other profile fields as needed
