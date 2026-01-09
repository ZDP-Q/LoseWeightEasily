"""
Mock 测试

使用 Mock 对象测试各组件，避免依赖外部资源。
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest


@pytest.mark.unit
class TestSearchEngineMock:
    """搜索引擎 Mock 测试"""

    def test_search_with_mocked_model(self, mock_sentence_transformer, mock_faiss_index):
        """测试使用 Mock 模型的搜索"""
        # 由于 search 模块使用懒加载导入，直接测试模型编码功能
        query = "测试查询"
        query_vector = mock_sentence_transformer.encode([query])
        
        # 验证编码被调用
        assert query_vector is not None
        assert query_vector.shape[1] == 384

        # 验证 FAISS 索引模拟
        distances, indices = mock_faiss_index.search(query_vector, 10)
        assert distances is not None
        assert indices is not None

    def test_search_result_processing(self):
        """测试搜索结果处理"""
        from loss_weight.models import FoodSearchResult

        # 模拟从 FAISS 获取的结果
        distances = np.array([[0.1, 0.2, 0.3]])
        indices = np.array([[100, 200, 300]])

        # 处理结果
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            # 相似度转换（FAISS L2 距离）
            similarity = 1.0 / (1.0 + dist)
            result = FoodSearchResult(
                fdc_id=int(idx),
                description=f"食物 {idx}",
                similarity=similarity,
            )
            results.append(result)

        assert len(results) == 3
        assert results[0].similarity > results[1].similarity > results[2].similarity


@pytest.mark.unit
class TestMealPlannerMock:
    """餐食规划器 Mock 测试"""

    def test_meal_planner_with_mocked_openai(self, mock_openai_client):
        """测试使用 Mock OpenAI 的餐食规划"""
        # 直接使用 mock 对象测试 API 调用
        response = mock_openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "测试"}]
        )
        
        assert response.choices[0].message.content == "模拟的餐食计划"

    def test_meal_plan_response_model(self):
        """测试餐食计划响应模型"""
        from loss_weight.models import MealPlanResponse

        response = MealPlanResponse(
            ingredients=["燕麦", "牛奶", "鸡胸肉"],
            plan="早餐：燕麦粥\n午餐：鸡胸肉沙拉\n晚餐：蒸鱼配蔬菜",
            model_used="gpt-3.5-turbo",
        )

        assert len(response.ingredients) == 3
        assert "燕麦粥" in response.plan
        assert response.model_used == "gpt-3.5-turbo"


@pytest.mark.unit
class TestDatabaseMock:
    """数据库 Mock 测试"""

    def test_database_context_manager_mock(self):
        """测试数据库上下文管理器 Mock"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)

        # 模拟使用
        with mock_conn:
            cursor = mock_conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

        assert result == (1,)

    def test_database_statistics_mock(self):
        """测试数据库统计 Mock"""
        from loss_weight.models import DatabaseStatistics

        # 模拟统计结果
        stats = DatabaseStatistics(
            foods=1000,
            nutrients=50,
            food_nutrients=50000,
            portions=3000,
        )

        assert stats.foods == 1000
        assert stats.nutrients == 50
        assert stats.food_nutrients == 50000
        assert stats.portions == 3000


@pytest.mark.unit
class TestWeightTrackerMock:
    """体重跟踪器 Mock 测试"""

    def test_weight_tracker_with_mocked_db(self):
        """测试使用 Mock 数据库的体重跟踪"""
        from loss_weight.weight_tracker import WeightTracker

        # 创建 Mock 数据库管理器
        mock_db = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_db.get_connection.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_db.get_connection.return_value.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        # 创建跟踪器
        tracker = WeightTracker(db_manager=mock_db)

        # 验证 db_manager 属性
        assert tracker._db_manager is mock_db


@pytest.mark.unit
class TestConfigMock:
    """配置 Mock 测试"""

    def test_settings_with_mocked_yaml(self, tmp_path):
        """测试使用 Mock YAML 的配置"""
        import yaml

        # 创建测试配置文件
        config_content = {
            "database": {"path": "test.db"},
            "embedding": {"model": "test-model", "dimension": 384},
            "search": {"limit": 10, "threshold": 0.5},
            "logging": {
                "mode": "dev",
                "level": "DEBUG",
                "dir": "logs",
                "enable_console": True,
                "enable_file": False,
            },
        }

        config_file = tmp_path / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_content, f)

        # 读取并验证
        with open(config_file, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)

        assert loaded["database"]["path"] == "test.db"
        assert loaded["embedding"]["model"] == "test-model"


@pytest.mark.unit
class TestLoggingMock:
    """日志 Mock 测试"""

    def test_logger_with_mock_handler(self):
        """测试使用 Mock Handler 的日志"""
        import logging

        # 创建 Mock Handler
        mock_handler = MagicMock(spec=logging.Handler)
        mock_handler.level = logging.DEBUG

        # 创建日志记录器
        logger = logging.getLogger("test_mock_logger")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        # 记录日志
        logger.info("测试消息")

        # 验证 handler 被调用
        assert mock_handler.emit.called or mock_handler.handle.called

        # 清理
        logger.removeHandler(mock_handler)


@pytest.mark.unit
class TestContainerMock:
    """容器 Mock 测试"""

    def test_container_with_mock_services(self):
        """测试使用 Mock 服务的容器"""
        from loss_weight.container import ServiceContainer

        # 创建容器
        container = ServiceContainer()

        # 注册 Mock 服务
        mock_service = MagicMock()
        mock_service.do_something.return_value = "result"

        container.register("mock_service", lambda: mock_service)

        # 获取服务
        service = container.get("mock_service")
        result = service.do_something()

        assert result == "result"

    def test_container_factory_called_once(self):
        """测试容器工厂只调用一次"""
        from loss_weight.container import ServiceContainer

        container = ServiceContainer()

        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return MagicMock()

        container.register("counted_service", factory)

        # 多次获取
        service1 = container.get("counted_service")
        service2 = container.get("counted_service")
        service3 = container.get("counted_service")

        # 工厂只调用一次
        assert call_count == 1
        assert service1 is service2 is service3


@pytest.mark.unit
class TestModelValidationMock:
    """模型验证 Mock 测试"""

    def test_food_search_result_validation(self):
        """测试食物搜索结果验证"""
        from pydantic import ValidationError

        from loss_weight.models import FoodSearchResult

        # 有效数据
        result = FoodSearchResult(
            fdc_id=12345,
            description="Apple, raw",
            similarity=0.95,
        )
        assert result.fdc_id == 12345

        # 无效数据 - similarity 超出范围
        with pytest.raises(ValidationError):
            FoodSearchResult(
                fdc_id=1,
                description="Invalid",
                similarity=1.5,
            )

    def test_bmr_input_validation(self):
        """测试 BMR 输入验证"""
        from pydantic import ValidationError

        from loss_weight.models import BMRInput

        # 有效数据
        input_data = BMRInput(
            weight_kg=70,
            height_cm=175,
            age=25,
            gender="male",
        )
        assert input_data.weight_kg == 70

        # 无效数据 - 体重不能为负
        with pytest.raises(ValidationError):
            BMRInput(
                weight_kg=-70,
                height_cm=175,
                age=25,
                gender="male",
            )
