"""
测试搜索引擎模块

注意：这些测试需要已初始化的数据库和模型。
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="module")
def search_engine():
    """获取搜索引擎实例（模块级别共享）"""
    from loss_weight.search import FoodSearchEngine
    from loss_weight.config import config
    
    if not config.database_exists():
        pytest.skip("数据库不存在，跳过搜索测试")
    
    engine = FoodSearchEngine()
    engine.ensure_index()
    return engine


class TestFoodSearchEngine:
    """食物搜索引擎测试"""
    
    def test_search_chinese(self, search_engine):
        """测试中文搜索"""
        results = search_engine.search("番茄")
        assert len(results) > 0
        
        # 检查结果结构
        fdc_id, description, category, similarity = results[0]
        assert isinstance(fdc_id, int)
        assert isinstance(description, str)
        assert isinstance(similarity, float)
    
    def test_search_english(self, search_engine):
        """测试英文搜索"""
        results = search_engine.search("tomato")
        assert len(results) > 0
    
    def test_search_with_limit(self, search_engine):
        """测试限制结果数量"""
        results = search_engine.search("beef", limit=3)
        assert len(results) <= 3
    
    def test_search_semantic(self, search_engine):
        """测试语义搜索（同义词）"""
        results_tomato = search_engine.search("番茄")
        results_xihongshi = search_engine.search("西红柿")
        
        # 两个搜索应该返回相似的结果
        if results_tomato and results_xihongshi:
            # 检查是否有交集
            ids_tomato = {r[0] for r in results_tomato}
            ids_xihongshi = {r[0] for r in results_xihongshi}
            assert len(ids_tomato & ids_xihongshi) > 0
    
    def test_search_with_details(self, search_engine):
        """测试搜索并返回详情"""
        results = search_engine.search_with_details("apple", limit=2)
        
        if results:
            result = results[0]
            assert "name" in result
            assert "category" in result
            assert "calories_per_100g" in result
            assert "similarity" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
