"""
测试配置模块
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loss_weight.config import Config, config


class TestConfig:
    """配置类测试"""
    
    def test_default_db_path(self):
        """测试默认数据库路径"""
        assert config.DB_PATH == "food_data.db"
    
    def test_default_embedding_model(self):
        """测试默认嵌入模型"""
        assert config.EMBEDDING_MODEL == "paraphrase-multilingual-MiniLM-L12-v2"
    
    def test_default_search_limit(self):
        """测试默认搜索限制"""
        assert config.DEFAULT_SEARCH_LIMIT == 10
    
    def test_similarity_threshold(self):
        """测试相似度阈值"""
        assert 0 < config.SIMILARITY_THRESHOLD < 1
    
    def test_get_json_data_path(self):
        """测试获取 JSON 数据路径"""
        path = Config.get_json_data_path()
        assert isinstance(path, Path)
        assert path.suffix == ".json"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
