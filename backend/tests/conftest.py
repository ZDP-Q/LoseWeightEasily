"""测试配置和共享 fixtures。

使用 SQLite 内存数据库运行测试，无需 PostgreSQL。
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import sys
from unittest.mock import MagicMock

# Mock heavy dependencies BEFORE importing app
sys.modules["sentence_transformers"] = MagicMock()
sys.modules["faiss"] = MagicMock()

from src.app import fastapi_server as app  # noqa: E402
from src.core.database import get_session  # noqa: E402


@pytest.fixture(name="session")
def session_fixture():
    """创建一个使用内存 SQLite 的测试数据库会话。"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """创建带依赖覆盖的 TestClient。"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
