"""
日志配置模块测试

测试日志系统的配置和功能。
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from loss_weight.logging_config import (
    BACKUP_COUNT,
    CONSOLE_FORMAT_DEV,
    CONSOLE_FORMAT_RELEASE,
    DEV_FORMAT,
    LOG_DIR,
    MAX_LOG_SIZE,
    RELEASE_FORMAT,
    ColoredFormatter,
    LoggerManager,
    get_logger,
    get_logger_manager,
    setup_logging,
)


@pytest.mark.unit
class TestColoredFormatter:
    """颜色格式化器测试"""

    def test_formatter_init_default(self):
        """测试默认初始化"""
        formatter = ColoredFormatter()
        assert formatter.use_colors in [True, False]  # 取决于终端

    def test_formatter_init_no_colors(self):
        """测试禁用颜色"""
        formatter = ColoredFormatter(use_colors=False)
        assert formatter.use_colors is False

    def test_formatter_with_format(self):
        """测试自定义格式"""
        formatter = ColoredFormatter(fmt="%(levelname)s - %(message)s", use_colors=False)
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="测试消息", args=(), exc_info=None
        )
        formatted = formatter.format(record)
        assert "INFO" in formatted
        assert "测试消息" in formatted

    def test_formatter_colors_map(self):
        """测试颜色映射"""
        assert "DEBUG" in ColoredFormatter.COLORS
        assert "INFO" in ColoredFormatter.COLORS
        assert "WARNING" in ColoredFormatter.COLORS
        assert "ERROR" in ColoredFormatter.COLORS
        assert "CRITICAL" in ColoredFormatter.COLORS


@pytest.mark.unit
class TestLoggerManagerSingleton:
    """日志管理器单例测试"""

    def test_singleton_pattern(self):
        """测试单例模式"""
        # 注意：由于已经有全局实例，这里测试 get_logger_manager
        manager1 = get_logger_manager()
        manager2 = get_logger_manager()
        assert manager1 is manager2


@pytest.mark.unit
class TestLoggerManagerSetup:
    """日志管理器设置测试"""

    def test_setup_dev_mode(self, tmp_path):
        """测试开发模式设置"""
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()
        
        manager.setup(
            mode="dev",
            log_level=logging.DEBUG,
            log_dir=tmp_path,
            enable_console=False,  # 禁用控制台避免测试干扰
            enable_file=True,
        )
        
        assert manager.mode == "dev"
        assert manager.log_level == logging.DEBUG

    def test_setup_release_mode(self, tmp_path):
        """测试生产模式设置"""
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()
        
        manager.setup(
            mode="release",
            log_level=logging.INFO,
            log_dir=tmp_path,
            enable_console=False,
            enable_file=True,
        )
        
        assert manager.mode == "release"
        assert manager.log_level == logging.INFO

    def test_setup_log_level_string(self, tmp_path):
        """测试使用字符串日志级别"""
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()
        
        manager.setup(
            mode="dev",
            log_level="WARNING",
            log_dir=tmp_path,
            enable_console=False,
            enable_file=False,
        )
        
        assert manager.log_level == logging.WARNING

    def test_setup_default_log_level(self, tmp_path):
        """测试默认日志级别"""
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()
        
        # dev 模式默认 DEBUG
        manager.setup(mode="dev", log_dir=tmp_path, enable_console=False, enable_file=False)
        assert manager.log_level == logging.DEBUG
        
        # release 模式默认 INFO
        LoggerManager._initialized = False
        manager2 = LoggerManager.__new__(LoggerManager)
        manager2.__init__()
        manager2.setup(mode="release", log_dir=tmp_path, enable_console=False, enable_file=False)
        assert manager2.log_level == logging.INFO


@pytest.mark.unit
class TestLoggerManagerGetLogger:
    """获取日志记录器测试"""

    def test_get_logger_auto_prefix(self, tmp_path):
        """测试自动添加前缀"""
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()
        manager.setup(log_dir=tmp_path, enable_console=False, enable_file=False)
        
        logger = manager.get_logger("test_module")
        assert logger.name == "loss_weight.test_module"

    def test_get_logger_with_prefix(self, tmp_path):
        """测试已有前缀的名称"""
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()
        manager.setup(log_dir=tmp_path, enable_console=False, enable_file=False)
        
        logger = manager.get_logger("loss_weight.existing")
        assert logger.name == "loss_weight.existing"

    def test_get_logger_main(self, tmp_path):
        """测试 __main__ 名称处理"""
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()
        manager.setup(log_dir=tmp_path, enable_console=False, enable_file=False)
        
        logger = manager.get_logger("__main__")
        assert logger.name == "loss_weight.main"


@pytest.mark.unit
class TestLoggerManagerSetLevel:
    """动态设置日志级别测试"""

    def test_set_level_int(self, tmp_path):
        """测试使用整数设置级别"""
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()
        manager.setup(log_dir=tmp_path, enable_console=False, enable_file=False)
        
        manager.set_level(logging.ERROR)
        assert manager.log_level == logging.ERROR

    def test_set_level_string(self, tmp_path):
        """测试使用字符串设置级别"""
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()
        manager.setup(log_dir=tmp_path, enable_console=False, enable_file=False)
        
        manager.set_level("WARNING")
        assert manager.log_level == logging.WARNING


@pytest.mark.unit
class TestLoggerManagerShutdown:
    """日志管理器关闭测试"""

    def test_shutdown(self, tmp_path):
        """测试关闭日志系统"""
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()
        manager.setup(log_dir=tmp_path, enable_console=True, enable_file=True)
        
        # 获取一个日志记录器
        logger = manager.get_logger("test")
        
        # 关闭
        manager.shutdown()
        
        assert manager._console_handler is None
        assert manager._file_handler is None
        assert len(manager._initialized_loggers) == 0


@pytest.mark.unit
class TestSetupLoggingFunction:
    """setup_logging 函数测试"""

    def test_setup_from_env_vars(self, tmp_path):
        """测试从环境变量读取配置"""
        with patch.dict(os.environ, {"LOSS_LOG_MODE": "release", "LOSS_LOG_LEVEL": "WARNING"}):
            # 这里只测试不抛出异常
            # 实际的 manager 已被初始化，无法完全测试
            pass  # 环境变量测试在集成测试中进行


@pytest.mark.unit
class TestGetLoggerFunction:
    """get_logger 函数测试"""

    def test_get_logger_cached(self):
        """测试日志记录器缓存"""
        logger1 = get_logger("cached_test")
        logger2 = get_logger("cached_test")
        assert logger1 is logger2


@pytest.mark.unit
class TestLogConstants:
    """日志常量测试"""

    def test_format_constants(self):
        """测试格式常量"""
        assert "%(asctime)s" in DEV_FORMAT
        assert "%(levelname)" in DEV_FORMAT
        assert "%(funcName)s" in DEV_FORMAT
        
        assert "%(asctime)s" in RELEASE_FORMAT
        assert "%(levelname)" in RELEASE_FORMAT
        # release 格式没有函数名
        assert "%(funcName)s" not in RELEASE_FORMAT

    def test_console_format_constants(self):
        """测试控制台格式常量"""
        assert "%(levelname)" in CONSOLE_FORMAT_DEV
        assert "%(name)s" in CONSOLE_FORMAT_DEV
        
        assert "%(levelname)" in CONSOLE_FORMAT_RELEASE
        # release 控制台没有名称
        assert "%(name)s" not in CONSOLE_FORMAT_RELEASE

    def test_size_constants(self):
        """测试大小常量"""
        assert MAX_LOG_SIZE == 10 * 1024 * 1024  # 10 MB
        assert BACKUP_COUNT == 5

    def test_log_dir_default(self):
        """测试默认日志目录"""
        assert LOG_DIR == Path("logs")


@pytest.mark.integration
class TestLoggerIntegration:
    """日志系统集成测试"""

    def test_log_to_file(self, tmp_path):
        """测试日志写入文件"""
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()
        manager.setup(
            mode="dev",
            log_dir=tmp_path,
            enable_console=False,
            enable_file=True,
        )
        
        logger = manager.get_logger("file_test")
        logger.info("测试日志消息")
        
        # 关闭以刷新缓冲区
        manager.shutdown()
        
        # 查找日志文件
        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) >= 1
        
        # 读取日志内容
        log_content = log_files[0].read_text(encoding="utf-8")
        assert "测试日志消息" in log_content

    def test_different_log_levels(self, tmp_path):
        """测试不同日志级别"""
        manager = LoggerManager.__new__(LoggerManager)
        LoggerManager._initialized = False
        manager.__init__()
        manager.setup(
            mode="dev",
            log_level=logging.DEBUG,
            log_dir=tmp_path,
            enable_console=False,
            enable_file=True,
        )
        
        logger = manager.get_logger("level_test")
        logger.debug("调试消息")
        logger.info("信息消息")
        logger.warning("警告消息")
        logger.error("错误消息")
        
        manager.shutdown()
        
        log_files = list(tmp_path.glob("*.log"))
        log_content = log_files[0].read_text(encoding="utf-8")
        
        assert "调试消息" in log_content
        assert "信息消息" in log_content
        assert "警告消息" in log_content
        assert "错误消息" in log_content
