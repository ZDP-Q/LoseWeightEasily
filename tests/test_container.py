"""
依赖注入容器模块测试

测试服务容器和依赖注入功能。
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from loss_weight.container import (
    ServiceContainer,
    get_container,
    get_database,
    get_logger,
    get_meal_planner,
    get_search_engine,
    get_settings,
    get_weight_tracker,
    reset_container,
)


@pytest.mark.unit
class TestServiceContainerInit:
    """服务容器初始化测试"""

    def test_init_default(self):
        """测试默认初始化"""
        container = ServiceContainer()
        assert container._settings is None
        assert container._instances == {}
        assert container._factories == {}

    def test_init_with_settings(self):
        """测试带配置初始化"""
        mock_settings = MagicMock()
        container = ServiceContainer(settings=mock_settings)
        assert container._settings is mock_settings


@pytest.mark.unit
class TestServiceContainerSettings:
    """服务容器配置访问测试"""

    def test_settings_lazy_load(self, reset_container_fixture):
        """测试配置懒加载"""
        container = ServiceContainer()
        # 访问 settings 属性
        settings = container.settings
        assert settings is not None

    def test_settings_from_init(self):
        """测试从初始化获取配置"""
        mock_settings = MagicMock()
        container = ServiceContainer(settings=mock_settings)
        assert container.settings is mock_settings


@pytest.mark.unit
class TestServiceContainerCustomServices:
    """自定义服务测试"""

    def test_register_service(self):
        """测试注册自定义服务"""
        container = ServiceContainer()
        
        def factory():
            return "custom_service_value"
        
        container.register("custom", factory)
        assert "custom" in container._factories

    def test_get_custom_service(self):
        """测试获取自定义服务"""
        container = ServiceContainer()
        
        call_count = 0
        def factory():
            nonlocal call_count
            call_count += 1
            return {"value": call_count}
        
        container.register("custom", factory)
        
        # 第一次获取
        service1 = container.get("custom")
        assert service1["value"] == 1
        
        # 第二次获取应该返回缓存的实例
        service2 = container.get("custom")
        assert service2["value"] == 1
        assert service1 is service2

    def test_get_unregistered_service_raises(self):
        """测试获取未注册服务抛出异常"""
        container = ServiceContainer()
        
        with pytest.raises(KeyError) as exc_info:
            container.get("nonexistent")
        
        assert "nonexistent" in str(exc_info.value)


@pytest.mark.unit
class TestServiceContainerReset:
    """服务容器重置测试"""

    def test_reset_clears_instances(self):
        """测试重置清除自定义实例"""
        container = ServiceContainer()
        container.register("test", lambda: "value")
        container.get("test")
        
        assert "test" in container._instances
        
        container.reset()
        
        assert container._instances == {}

    def test_reset_clears_logging_flag(self):
        """测试重置清除日志标志"""
        container = ServiceContainer()
        container._logging_initialized = True
        
        container.reset()
        
        assert container._logging_initialized is False


@pytest.mark.unit
class TestGlobalContainerFunctions:
    """全局容器函数测试"""

    def test_get_container_singleton(self, reset_container_fixture):
        """测试容器单例"""
        container1 = get_container()
        container2 = get_container()
        assert container1 is container2

    def test_reset_container(self, reset_container_fixture):
        """测试重置全局容器"""
        container1 = get_container()
        reset_container()
        container2 = get_container()
        
        # 重置后应该是新实例
        assert container1 is not container2


@pytest.mark.unit
class TestServiceAccessFunctions:
    """服务访问便捷函数测试"""

    def test_get_settings_function(self, reset_container_fixture):
        """测试 get_settings 函数"""
        settings = get_settings()
        assert settings is not None

    def test_get_logger_function(self, reset_container_fixture):
        """测试 get_logger 函数"""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)


@pytest.mark.integration
class TestServiceContainerLazyLoading:
    """服务懒加载集成测试"""

    def test_database_lazy_load(self, reset_container_fixture, tmp_path, monkeypatch):
        """测试数据库管理器懒加载"""
        # 设置临时数据库路径
        mock_settings = MagicMock()
        mock_settings.database.path = str(tmp_path / "test.db")
        mock_settings.logging.mode = "dev"
        mock_settings.logging.level = "DEBUG"
        mock_settings.logging.dir = str(tmp_path / "logs")
        mock_settings.logging.enable_console = False
        mock_settings.logging.enable_file = False
        
        container = ServiceContainer(settings=mock_settings)
        
        # 访问前不存在
        assert "database" not in container.__dict__
        
        # 访问触发加载
        db = container.database
        assert db is not None

    def test_weight_tracker_lazy_load(self, reset_container_fixture, tmp_path):
        """测试体重跟踪器懒加载"""
        mock_settings = MagicMock()
        mock_settings.database.path = str(tmp_path / "test.db")
        mock_settings.logging.mode = "dev"
        mock_settings.logging.level = "DEBUG"
        mock_settings.logging.dir = str(tmp_path / "logs")
        mock_settings.logging.enable_console = False
        mock_settings.logging.enable_file = False
        
        container = ServiceContainer(settings=mock_settings)
        
        # 访问前不存在
        assert "weight_tracker" not in container.__dict__
        
        # 访问触发加载
        tracker = container.weight_tracker
        assert tracker is not None


@pytest.mark.unit
class TestContainerLogger:
    """容器日志功能测试"""

    def test_get_logger_returns_logger(self, reset_container_fixture):
        """测试获取日志记录器"""
        container = get_container()
        logger = container.get_logger("test.module")
        
        assert isinstance(logger, logging.Logger)

    def test_get_logger_consistent_name(self, reset_container_fixture):
        """测试日志记录器名称一致性"""
        container = get_container()
        logger1 = container.get_logger("same_module")
        logger2 = container.get_logger("same_module")
        
        assert logger1.name == logger2.name


@pytest.mark.unit
class TestContainerEnsureMethods:
    """容器确保方法测试"""

    def test_ensure_database_creates_tables(self, reset_container_fixture, tmp_path):
        """测试 ensure_database 创建表"""
        mock_settings = MagicMock()
        mock_settings.database.path = str(tmp_path / "test.db")
        mock_settings.logging.mode = "dev"
        mock_settings.logging.level = "DEBUG"
        mock_settings.logging.dir = str(tmp_path / "logs")
        mock_settings.logging.enable_console = False
        mock_settings.logging.enable_file = False
        
        container = ServiceContainer(settings=mock_settings)
        container.ensure_database()
        
        # 验证数据库文件存在
        db_path = tmp_path / "test.db"
        assert db_path.exists()
