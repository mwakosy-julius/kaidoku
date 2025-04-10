from typing import Optional

from sqlalchemy import table
from sqlmodel import SQLModel, Field

class SettingsBase(SQLModel):
    project_name: str
    api_v_str: str
    settings_id: int | None = Field(default=None, foreign_key="settings.id")


class Settings(SettingsBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # database
    postgres_server: str
    postgres_port: int = Field(default=5432)
    postgres_user: str
    postgres_password: str
    postgres_db: str
