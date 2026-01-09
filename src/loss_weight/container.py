"""
依赖注入容器

提供统一的服务管理和依赖注入功能，支持懒加载以提升启动速度。
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from functools import cached_property
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from .config import Settings
    from .database import DatabaseManager
    from .logging_config import LoggerManager
    from .meal_planner import MealPlanner
    from .search import FoodSearchEngine
    from .weight_tracker import WeightTracker

T = TypeVar("T")


class ServiceContainer:
    """
    服务容器 - 依赖注入实现

    使用懒加载模式，只在首次访问时创建服务实例。
    支持依赖注入和服务生命周期管理。
    """

    def __init__(self, settings: Settings | None = None):
        """
        初始化服务容器

        Args:
            settings: 配置实例，如果不提供则使用默认配置
        """
        self._settings = settings
        self._instances: dict[str, Any] = {}
        self._factories: dict[str, Callable[[], Any]] = {}
        self._logging_initialized = False

    @cached_property
    def settings(self) -> Settings:
        """获取配置实例（懒加载）"""
        if self._settings is not None:
            return self._settings

        # 懒加载导入
        from .config import get_settings

        return get_settings()

    @cached_property
    def logger_manager(self) -> LoggerManager:
        """获取日志管理器实例（懒加载）"""
        from .logging_config import get_logger_manager, setup_logging

        if not self._logging_initialized:
            # 从配置初始化日志系统
            log_config = self.settings.logging
            setup_logging(
                mode=log_config.mode,
                log_level=log_config.level,
                log_dir=log_config.dir,
                enable_console=log_config.enable_console,
                enable_file=log_config.enable_file,
            )
            self._logging_initialized = True

        return get_logger_manager()

    def get_logger(self, name: str) -> logging.Logger:
        """
        获取日志记录器

        Args:
            name: 模块名称，通常使用 __name__

        Returns:
            配置好的日志记录器
        """
        return self.logger_manager.get_logger(name)

    @cached_property
    def database(self) -> DatabaseManager:
        """获取数据库管理器实例（懒加载）"""
        from .database import DatabaseManager

        return DatabaseManager(self.settings.database.path)

    @cached_property
    def search_engine(self) -> FoodSearchEngine:
        """获取搜索引擎实例（懒加载）"""
        from .search import FoodSearchEngine

        return FoodSearchEngine(db_manager=self.database, settings=self.settings)

    @cached_property
    def weight_tracker(self) -> WeightTracker:
        """获取体重跟踪器实例（懒加载）"""
        from .weight_tracker import WeightTracker

        return WeightTracker(db_manager=self.database)

    @cached_property
    def meal_planner(self) -> MealPlanner:
        """获取餐食规划器实例（懒加载）"""
        from .meal_planner import MealPlanner

        return MealPlanner(db_manager=self.database, settings=self.settings)

    def register(self, name: str, factory: Callable[[], T]) -> None:
        """
        注册自定义服务工厂

        Args:
            name: 服务名称
            factory: 创建服务实例的工厂函数
        """
        self._factories[name] = factory

    def get(self, name: str) -> Any:
        """
        获取自定义服务实例

        Args:
            name: 服务名称

        Returns:
            服务实例

        Raises:
            KeyError: 服务未注册
        """
        if name not in self._instances:
            if name not in self._factories:
                raise KeyError(f"服务 '{name}' 未注册")
            self._instances[name] = self._factories[name]()
        return self._instances[name]

    def reset(self) -> None:
        """重置所有缓存的服务实例"""
        # 清除 cached_property 缓存
        for attr in [
            "settings",
            "database",
            "search_engine",
            "weight_tracker",
            "meal_planner",
            "logger_manager",
        ]:
            if attr in self.__dict__:
                del self.__dict__[attr]

        # 清除自定义服务
        self._instances.clear()
        self._logging_initialized = False

    def ensure_database(self) -> None:
        """确保数据库已初始化"""
        self.database.create_tables()

    def ensure_index(self) -> None:
        """确保搜索索引已构建"""
        self.search_engine.ensure_index()


# 全局容器实例（单例模式）
_container: ServiceContainer | None = None


def get_container(settings: Settings | None = None) -> ServiceContainer:
    """
    获取全局服务容器实例

    Args:
        settings: 可选的配置实例

    Returns:
        ServiceContainer 实例
    """
    global _container
    if _container is None:
        _container = ServiceContainer(settings)
    return _container


def reset_container() -> None:
    """重置全局容器（主要用于测试）"""
    global _container
    if _container is not None:
        _container.reset()
    _container = None


# 便捷访问函数
def get_database() -> DatabaseManager:
    """获取数据库管理器"""
    return get_container().database


def get_search_engine() -> FoodSearchEngine:
    """获取搜索引擎"""
    return get_container().search_engine


def get_weight_tracker() -> WeightTracker:
    """获取体重跟踪器"""
    return get_container().weight_tracker


def get_meal_planner() -> MealPlanner:
    """获取餐食规划器"""
    return get_container().meal_planner


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器的便捷函数

    Args:
        name: 模块名称，通常使用 __name__

    Returns:
        配置好的日志记录器

    使用示例:
        from loss_weight.container import get_logger
        logger = get_logger(__name__)
        logger.info("操作完成")
    """
    return get_container().get_logger(name)


def get_settings() -> Settings:
    """获取配置"""
    return get_container().settings
