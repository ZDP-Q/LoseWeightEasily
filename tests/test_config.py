"""
测试配置模块
"""

import sys
from pathlib import Path

import pytest

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loss_weight.config import Settings, get_settings


class TestSettings:
    """配置类测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前清除缓存"""
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()

    def test_default_db_path(self):
        """测试默认数据库路径"""
        settings = get_settings()
        assert settings.DB_PATH == "food_data.db"

    def test_default_embedding_model(self):
        """测试默认嵌入模型"""
        settings = get_settings()
        assert settings.embedding.model == "paraphrase-multilingual-MiniLM-L12-v2"

    def test_default_search_limit(self):
        """测试默认搜索限制"""
        settings = get_settings()
        assert settings.search.limit == 10

    def test_similarity_threshold(self):
        """测试相似度阈值"""
        settings = get_settings()
        assert 0 < settings.search.threshold < 1

    def test_get_json_data_path(self):
        """测试获取 JSON 数据路径"""
        settings = get_settings()
        path = settings.get_json_data_path()
        assert isinstance(path, Path)
        assert path.suffix == ".json"

    def test_settings_singleton(self):
        """测试配置单例模式"""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_backward_compatibility_properties(self):
        """测试向后兼容性属性"""
        settings = get_settings()
        # 这些属性应该与旧的 config 对象兼容
        assert hasattr(settings, "DB_PATH")
        assert hasattr(settings, "EMBEDDING_MODEL")
        assert hasattr(settings, "DEFAULT_SEARCH_LIMIT")
        assert hasattr(settings, "SIMILARITY_THRESHOLD")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
