"""
Pytest 配置和共享 fixtures

提供测试所需的通用配置和 fixtures。
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Generator
from unittest.mock import MagicMock

import pytest

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

if TYPE_CHECKING:
    from loss_weight.config import Settings
    from loss_weight.database import DatabaseManager


# ============================================================================
# 全局配置
# ============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Pytest 配置钩子"""
    # 注册自定义标记
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "e2e: 端到端测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "requires_db: 需要真实数据库")
    config.addinivalue_line("markers", "requires_model: 需要嵌入模型")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """设置测试环境"""
    # 设置测试环境变量
    os.environ["LOSS_LOGGING__MODE"] = "dev"
    os.environ["LOSS_LOGGING__LEVEL"] = "WARNING"  # 测试时减少日志输出
    os.environ["LOSS_LOGGING__ENABLE_CONSOLE"] = "false"
    os.environ["LOSS_LOGGING__ENABLE_FILE"] = "false"

    yield

    # 清理环境变量
    for key in ["LOSS_LOGGING__MODE", "LOSS_LOGGING__LEVEL", 
                "LOSS_LOGGING__ENABLE_CONSOLE", "LOSS_LOGGING__ENABLE_FILE"]:
        os.environ.pop(key, None)


# ============================================================================
# 配置 Fixtures
# ============================================================================


@pytest.fixture
def reset_settings() -> Generator[None, None, None]:
    """重置配置缓存"""
    from loss_weight.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def settings(reset_settings: None) -> Settings:
    """获取配置实例"""
    from loss_weight.config import get_settings

    return get_settings()


# ============================================================================
# 数据库 Fixtures
# ============================================================================


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """创建临时数据库路径"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    yield db_path

    # 清理
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def temp_db(temp_db_path: str) -> Generator[DatabaseManager, None, None]:
    """创建带有表结构的临时数据库"""
    from loss_weight.database import DatabaseManager

    db_manager = DatabaseManager(temp_db_path)
    db_manager.create_tables()
    yield db_manager


@pytest.fixture
def temp_db_with_weight_table(temp_db_path: str) -> Generator[DatabaseManager, None, None]:
    """创建带有体重记录表的临时数据库"""
    from loss_weight.database import DatabaseManager

    db_manager = DatabaseManager(temp_db_path)
    db_manager.create_tables()

    # 创建体重记录表
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weight_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight_kg REAL NOT NULL,
                recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)
        conn.commit()

    yield db_manager


# ============================================================================
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_sentence_transformer() -> MagicMock:
    """Mock SentenceTransformer 模型"""
    import numpy as np

    mock_model = MagicMock()
    # 返回固定维度的向量
    mock_model.encode.return_value = np.random.rand(1, 384).astype(np.float32)
    mock_model.get_sentence_embedding_dimension.return_value = 384
    return mock_model


@pytest.fixture
def mock_faiss_index() -> MagicMock:
    """Mock FAISS 索引"""
    import numpy as np

    mock_index = MagicMock()
    mock_index.ntotal = 100
    # 返回模拟的搜索结果
    mock_index.search.return_value = (
        np.array([[0.9, 0.8, 0.7]]),  # distances
        np.array([[0, 1, 2]]),  # indices
    )
    return mock_index


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Mock OpenAI 客户端"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "模拟的餐食计划"
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


# ============================================================================
# 容器 Fixtures
# ============================================================================


@pytest.fixture
def reset_container_fixture() -> Generator[None, None, None]:
    """重置服务容器"""
    from loss_weight.container import reset_container as _reset_container

    _reset_container()
    yield
    _reset_container()


# ============================================================================
# 真实数据 Fixtures（需要初始化的数据库）
# ============================================================================


@pytest.fixture(scope="module")
def real_settings() -> Settings:
    """获取真实配置（模块级别）"""
    from loss_weight.config import get_settings

    get_settings.cache_clear()
    return get_settings()


@pytest.fixture(scope="module")
def real_db_available(real_settings: Settings) -> bool:
    """检查真实数据库是否可用"""
    return real_settings.database_exists()


@pytest.fixture(scope="module")
def real_search_engine(real_settings: Settings, real_db_available: bool):
    """获取真实搜索引擎实例（模块级别）"""
    if not real_db_available:
        pytest.skip("数据库不存在，跳过真实搜索引擎测试")

    from loss_weight.search import FoodSearchEngine

    engine = FoodSearchEngine()
    engine.ensure_index()
    return engine
