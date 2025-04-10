from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
