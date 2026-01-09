"""
日志配置模块

提供全局日志记录器，支持开发模式和生产模式区分。
- 开发模式 (DEBUG): 详细的控制台输出 + 文件日志
- 生产模式 (RELEASE): 简洁的控制台输出 + 文件日志

日志级别:
- DEBUG: 调试信息，仅开发模式显示
- INFO: 一般运行信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

# 日志格式
DEV_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
RELEASE_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
CONSOLE_FORMAT_DEV = "%(levelname)-8s | %(name)s | %(message)s"
CONSOLE_FORMAT_RELEASE = "%(levelname)-8s | %(message)s"

# 日志目录
LOG_DIR = Path("logs")

# 日志文件大小限制 (10 MB)
MAX_LOG_SIZE = 10 * 1024 * 1024

# 日志文件保留数量
BACKUP_COUNT = 5


class ColoredFormatter(logging.Formatter):
    """带颜色的控制台日志格式化器"""

    # ANSI 颜色代码
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    def __init__(self, fmt: str | None = None, use_colors: bool = True):
        super().__init__(fmt, datefmt="%H:%M:%S")
        self.use_colors = use_colors and self._supports_color()

    @staticmethod
    def _supports_color() -> bool:
        """检测终端是否支持颜色"""
        # Windows 10+ 支持 ANSI
        if sys.platform == "win32":
            try:
                import ctypes

                kernel32 = ctypes.windll.kernel32
                # 启用 ANSI 支持
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except Exception:
                return os.environ.get("TERM") is not None
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        if self.use_colors and record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


class LoggerManager:
    """
    日志管理器

    管理全局日志配置，支持开发和生产两种模式。

    使用方式:
        from loss_weight.logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("这是一条信息")
    """

    _instance: LoggerManager | None = None
    _initialized: bool = False

    def __new__(cls) -> LoggerManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if LoggerManager._initialized:
            return
        LoggerManager._initialized = True

        self._mode: Literal["dev", "release"] = "dev"
        self._root_logger: logging.Logger | None = None
        self._log_level: int = logging.DEBUG
        self._console_handler: logging.Handler | None = None
        self._file_handler: logging.Handler | None = None
        self._initialized_loggers: set[str] = set()

    @property
    def mode(self) -> Literal["dev", "release"]:
        """获取当前日志模式"""
        return self._mode

    @property
    def log_level(self) -> int:
        """获取当前日志级别"""
        return self._log_level

    def setup(
        self,
        mode: Literal["dev", "release"] = "dev",
        log_level: int | str | None = None,
        log_dir: Path | str | None = None,
        enable_console: bool = True,
        enable_file: bool = True,
    ) -> None:
        """
        配置日志系统

        Args:
            mode: 日志模式 ("dev" 开发模式, "release" 生产模式)
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: 日志文件目录
            enable_console: 是否启用控制台输出
            enable_file: 是否启用文件日志
        """
        self._mode = mode

        # 设置日志级别
        if log_level is None:
            self._log_level = logging.DEBUG if mode == "dev" else logging.INFO
        elif isinstance(log_level, str):
            self._log_level = getattr(logging, log_level.upper(), logging.INFO)
        else:
            self._log_level = log_level

        # 日志目录
        log_path = Path(log_dir) if log_dir else LOG_DIR

        # 获取根日志记录器
        self._root_logger = logging.getLogger("loss_weight")
        self._root_logger.setLevel(logging.DEBUG)  # 根记录器接收所有级别

        # 清除现有处理器
        self._root_logger.handlers.clear()

        # 添加控制台处理器
        if enable_console:
            self._setup_console_handler()

        # 添加文件处理器
        if enable_file:
            self._setup_file_handler(log_path)

        # 记录初始化信息
        self._root_logger.debug(
            f"日志系统初始化完成 | 模式: {mode} | 级别: {logging.getLevelName(self._log_level)}"
        )

    def _setup_console_handler(self) -> None:
        """设置控制台日志处理器"""
        self._console_handler = logging.StreamHandler(sys.stdout)

        # 控制台日志级别
        console_level = self._log_level if self._mode == "dev" else logging.INFO
        self._console_handler.setLevel(console_level)

        # 格式化器
        fmt = CONSOLE_FORMAT_DEV if self._mode == "dev" else CONSOLE_FORMAT_RELEASE
        formatter = ColoredFormatter(fmt)
        self._console_handler.setFormatter(formatter)

        if self._root_logger:
            self._root_logger.addHandler(self._console_handler)

    def _setup_file_handler(self, log_dir: Path) -> None:
        """设置文件日志处理器"""
        # 确保日志目录存在
        log_dir.mkdir(parents=True, exist_ok=True)

        # 生成日志文件名
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"loss_weight_{date_str}.log"

        # 使用 RotatingFileHandler 管理日志文件大小
        self._file_handler = RotatingFileHandler(
            log_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )

        # 文件日志记录所有级别 (DEBUG 以上)
        self._file_handler.setLevel(logging.DEBUG)

        # 格式化器 - 文件日志使用详细格式
        fmt = DEV_FORMAT if self._mode == "dev" else RELEASE_FORMAT
        formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
        self._file_handler.setFormatter(formatter)

        if self._root_logger:
            self._root_logger.addHandler(self._file_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """
        获取命名日志记录器

        Args:
            name: 日志记录器名称，通常使用 __name__

        Returns:
            配置好的日志记录器
        """
        # 确保日志系统已初始化
        if self._root_logger is None:
            self.setup()

        # 规范化名称
        if name.startswith("loss_weight."):
            logger_name = name
        elif name == "__main__":
            logger_name = "loss_weight.main"
        else:
            logger_name = f"loss_weight.{name}"

        logger = logging.getLogger(logger_name)

        # 首次获取时设置级别
        if logger_name not in self._initialized_loggers:
            logger.setLevel(self._log_level)
            self._initialized_loggers.add(logger_name)

        return logger

    def set_level(self, level: int | str) -> None:
        """
        动态设置日志级别

        Args:
            level: 日志级别
        """
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)

        self._log_level = level

        if self._root_logger:
            self._root_logger.setLevel(level)

        # 更新控制台处理器级别
        if self._console_handler and self._mode == "dev":
            self._console_handler.setLevel(level)

        # 更新所有已初始化的日志记录器
        for name in self._initialized_loggers:
            logging.getLogger(name).setLevel(level)

    def shutdown(self) -> None:
        """关闭日志系统"""
        if self._root_logger:
            for handler in self._root_logger.handlers[:]:
                handler.close()
                self._root_logger.removeHandler(handler)

        self._console_handler = None
        self._file_handler = None
        self._initialized_loggers.clear()


# 全局日志管理器实例
_logger_manager: LoggerManager | None = None


def get_logger_manager() -> LoggerManager:
    """获取日志管理器实例"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager


def setup_logging(
    mode: Literal["dev", "release"] | None = None,
    log_level: int | str | None = None,
    log_dir: Path | str | None = None,
    enable_console: bool = True,
    enable_file: bool = True,
) -> None:
    """
    初始化日志系统

    Args:
        mode: 日志模式 ("dev" 或 "release")，默认从环境变量 LOSS_LOG_MODE 读取
        log_level: 日志级别，默认从环境变量 LOSS_LOG_LEVEL 读取
        log_dir: 日志目录，默认 "logs"
        enable_console: 是否启用控制台输出
        enable_file: 是否启用文件日志
    """
    # 从环境变量读取默认值
    if mode is None:
        env_mode = os.environ.get("LOSS_LOG_MODE", "dev").lower()
        mode = "release" if env_mode == "release" else "dev"

    if log_level is None:
        log_level = os.environ.get("LOSS_LOG_LEVEL")

    manager = get_logger_manager()
    manager.setup(
        mode=mode,
        log_level=log_level,
        log_dir=log_dir,
        enable_console=enable_console,
        enable_file=enable_file,
    )


@lru_cache(maxsize=128)
def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器

    推荐在每个模块顶部调用:
        from loss_weight.logging_config import get_logger
        logger = get_logger(__name__)

    Args:
        name: 模块名称，通常使用 __name__

    Returns:
        配置好的日志记录器
    """
    return get_logger_manager().get_logger(name)


# 便捷的日志级别常量
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
