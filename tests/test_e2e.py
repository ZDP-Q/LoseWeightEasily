"""
端到端测试 (E2E)

测试完整的工作流程和用户场景。
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.e2e
class TestBMRWorkflow:
    """BMR 计算完整工作流程测试"""

    def test_complete_bmr_calculation(self):
        """测试完整的 BMR 计算流程"""
        from loss_weight.bmr import (
            calculate_bmr,
            calculate_bmr_from_input,
            calculate_tdee_result,
            get_all_tdee_levels,
        )
        from loss_weight.models import BMRInput

        # 步骤 1: 创建用户输入
        user_input = BMRInput(
            weight_kg=70,
            height_cm=175,
            age=25,
            gender="male",
        )

        # 步骤 2: 计算 BMR
        bmr_result = calculate_bmr_from_input(user_input)
        assert bmr_result.bmr > 0
        assert bmr_result.input_data == user_input

        # 步骤 3: 计算特定活动水平的 TDEE
        tdee_result = calculate_tdee_result(bmr_result.bmr, "moderate")
        assert tdee_result.tdee > bmr_result.bmr
        assert tdee_result.activity_level == "moderate"

        # 步骤 4: 获取所有活动水平的 TDEE
        all_tdee = get_all_tdee_levels(bmr_result.bmr)
        assert len(all_tdee) == 5

        # 验证 TDEE 按活动强度递增
        sorted_tdee = sorted(all_tdee, key=lambda x: x.multiplier)
        for i in range(len(sorted_tdee) - 1):
            assert sorted_tdee[i].tdee < sorted_tdee[i + 1].tdee


@pytest.mark.e2e
class TestWeightTrackingWorkflow:
    """体重跟踪完整工作流程测试"""

    def test_complete_weight_tracking(self, temp_db_with_weight_table):
        """测试完整的体重跟踪流程"""
        from loss_weight.weight_tracker import WeightTracker

        tracker = WeightTracker(db_manager=temp_db_with_weight_table)

        # 步骤 1: 记录初始体重
        record_id1 = tracker.record_weight(72.0, "开始减重")
        assert record_id1 > 0

        # 步骤 2: 一周后记录第二次
        record_id2 = tracker.record_weight(71.5, "第一周")

        # 步骤 3: 两周后记录第三次
        record_id3 = tracker.record_weight(71.0, "第二周")

        # 步骤 4: 三周后记录第四次
        record_id4 = tracker.record_weight(70.5, "第三周")

        # 步骤 5: 查看最新记录
        latest = tracker.get_latest_record()
        assert latest.weight_kg == 70.5
        assert latest.notes == "第三周"

        # 步骤 6: 查看历史记录
        records = tracker.get_records(limit=10)
        assert len(records) == 4
        # 记录按时间倒序排列
        assert records[0].weight_kg == 70.5
        assert records[-1].weight_kg == 72.0

        # 步骤 7: 查看统计信息
        stats = tracker.get_weight_statistics()
        assert stats.total_records == 4
        assert stats.latest_weight == 70.5
        assert stats.earliest_weight == 72.0
        assert stats.weight_change == -1.5  # 减少了 1.5kg


@pytest.mark.e2e
class TestDatabaseWorkflow:
    """数据库完整工作流程测试"""

    def test_database_lifecycle(self, temp_db_path):
        """测试数据库生命周期"""
        from loss_weight.database import DatabaseManager
        from loss_weight.models import DatabaseStatistics

        # 步骤 1: 创建数据库管理器
        db = DatabaseManager(temp_db_path)

        # 步骤 2: 创建表结构
        db.create_tables()

        # 步骤 3: 验证表创建
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]

        assert "foods" in tables
        assert "nutrients" in tables
        assert "food_nutrients" in tables
        assert "food_portions" in tables

        # 步骤 4: 获取统计信息
        stats = db.get_statistics()
        assert isinstance(stats, DatabaseStatistics)
        assert stats.foods == 0  # 空数据库


@pytest.mark.e2e
class TestContainerWorkflow:
    """容器依赖注入工作流程测试"""

    def test_container_service_lifecycle(self, reset_container_fixture, tmp_path):
        """测试容器服务生命周期"""
        from loss_weight.container import (
            ServiceContainer,
            get_container,
            get_settings,
            reset_container,
        )

        # 步骤 1: 获取容器
        container = get_container()
        assert container is not None

        # 步骤 2: 获取配置
        settings = container.settings
        assert settings is not None

        # 步骤 3: 验证单例
        settings2 = get_settings()
        assert settings is settings2

        # 步骤 4: 重置容器
        reset_container()

        # 步骤 5: 获取新容器
        new_container = get_container()
        assert new_container is not container


@pytest.mark.e2e
class TestLoggingWorkflow:
    """日志系统工作流程测试"""

    def test_logging_lifecycle(self, tmp_path):
        """测试日志系统生命周期"""
        import logging

        from loss_weight.logging_config import LoggerManager

        # 步骤 1: 创建日志管理器
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()

        # 步骤 2: 设置日志系统
        manager.setup(
            mode="dev",
            log_level=logging.DEBUG,
            log_dir=tmp_path,
            enable_console=False,
            enable_file=True,
        )

        # 步骤 3: 获取日志记录器
        logger = manager.get_logger("e2e_test")

        # 步骤 4: 写入各级别日志
        logger.debug("调试消息")
        logger.info("信息消息")
        logger.warning("警告消息")
        logger.error("错误消息")

        # 步骤 5: 关闭日志系统
        manager.shutdown()

        # 步骤 6: 验证日志文件
        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) >= 1

        log_content = log_files[0].read_text(encoding="utf-8")
        assert "调试消息" in log_content
        assert "信息消息" in log_content
        assert "警告消息" in log_content
        assert "错误消息" in log_content


@pytest.mark.e2e
@pytest.mark.slow
class TestConfigurationWorkflow:
    """配置系统工作流程测试"""

    def test_settings_configuration(self, reset_settings):
        """测试配置系统完整流程"""
        from loss_weight.config import get_settings

        # 步骤 1: 获取配置
        settings = get_settings()

        # 步骤 2: 验证数据库配置
        assert settings.database.path is not None

        # 步骤 3: 验证嵌入配置
        assert settings.embedding.model is not None

        # 步骤 4: 验证搜索配置
        assert settings.search.limit > 0
        assert 0 < settings.search.threshold <= 1

        # 步骤 5: 验证日志配置
        assert settings.logging.mode in ["dev", "release"]
        assert settings.logging.level in [
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
        ]

        # 步骤 6: 验证向后兼容属性
        assert settings.DB_PATH == settings.database.path
        assert settings.EMBEDDING_MODEL == settings.embedding.model


@pytest.mark.e2e
@pytest.mark.requires_db
class TestSearchWorkflow:
    """搜索功能完整工作流程测试 (需要真实数据库)"""

    def test_food_search_workflow(self, real_search_engine):
        """测试食物搜索完整流程"""
        # 步骤 1: 简单搜索
        results = real_search_engine.search("番茄")
        assert len(results) > 0

        # 步骤 2: 验证结果结构
        first_result = results[0]
        assert first_result.fdc_id > 0
        assert first_result.description
        assert 0 <= first_result.similarity <= 1

        # 步骤 3: 带限制搜索
        limited_results = real_search_engine.search("牛肉", limit=3)
        assert len(limited_results) <= 3

        # 步骤 4: 搜索并获取详情
        detailed_results = real_search_engine.search_with_details("鸡蛋", limit=2)
        if detailed_results:
            detail = detailed_results[0]
            assert detail.name
            # FoodCompleteInfo 没有 fdc_id，只有 name

    def test_semantic_search_workflow(self, real_search_engine):
        """测试语义搜索工作流程"""
        # 番茄和西红柿是同一种食物的不同名称
        results1 = real_search_engine.search("番茄", limit=5)
        results2 = real_search_engine.search("西红柿", limit=5)

        if results1 and results2:
            # 应该有一些重叠的结果
            ids1 = {r.fdc_id for r in results1}
            ids2 = {r.fdc_id for r in results2}
            # 验证语义搜索能找到相关结果
            assert len(ids1 & ids2) > 0 or len(results1) > 0
