from sqlmodel import create_engine, Session, SQLModel
from .config import get_settings

settings = get_settings()

engine = create_engine(settings.database.url)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
