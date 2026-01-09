"""
测试数据库模块
"""

import pytest
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loss_weight.database import DatabaseManager


class TestDatabaseManager:
    """数据库管理器测试"""
    
    @pytest.fixture
    def temp_db(self):
        """创建临时数据库"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # 清理
        Path(db_path).unlink(missing_ok=True)
    
    def test_create_tables(self, temp_db):
        """测试创建表结构"""
        db_manager = DatabaseManager(temp_db)
        db_manager.create_tables()
        
        # 验证表是否创建
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert "foods" in tables
        assert "nutrients" in tables
        assert "food_nutrients" in tables
        assert "food_portions" in tables
    
    def test_get_statistics_empty_db(self, temp_db):
        """测试空数据库统计"""
        db_manager = DatabaseManager(temp_db)
        db_manager.create_tables()
        
        stats = db_manager.get_statistics()
        
        assert stats["foods"] == 0
        assert stats["nutrients"] == 0
        assert stats["food_nutrients"] == 0
        assert stats["portions"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
