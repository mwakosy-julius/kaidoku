from datetime import datetime, timezone
from typing import Optional

from sqlmodel import (
    Field,
    Session,
    SQLModel,
    func,
    select,
)

from app.core.security import verify_password

from .database import engine


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(
        min_length=3,
        max_length=50,
        unique=True,
        description="Email Address",
        index=True,
    )
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )

    @classmethod
    def authenticate(cls, email: str, password: str):
        """Authenticate a user with email and password."""
        with Session(engine) as session:
            stmt = select(cls).where(cls.email == email)
            user = session.exec(stmt).first()
            if user and verify_password(password, user.hashed_password):
                return user

    @classmethod
    def by_email(cls, email: str):
        """Get a user by email."""
        with Session(engine) as session:
            return session.exec(select(cls).where(cls.email == email)).first()
