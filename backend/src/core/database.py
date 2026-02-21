from sqlalchemy import event
from sqlmodel import create_engine, Session, SQLModel
from .config import get_settings

settings = get_settings()

is_sqlite = settings.database.url.startswith("sqlite")

engine_kwargs = {
    "pool_pre_ping": True,
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # 针对 PostgreSQL 等生产级数据库进行连接池调优
    engine_kwargs.update({
        "pool_size": 20,          # 基础连接池大小
        "max_overflow": 10,       # 允许超出的连接数
        "pool_recycle": 3600,     # 连接回收时间（1小时）
    })

engine = create_engine(settings.database.url, **engine_kwargs)


if is_sqlite:

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA cache_size=-20000")
        cursor.close()


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
