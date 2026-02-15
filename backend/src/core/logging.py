"""日志系统初始化。

基于 LoggingSettings 配置，支持控制台 + 文件双输出。
"""

import logging
import sys
from pathlib import Path

from .config import get_settings


def setup_logging() -> None:
    """根据配置初始化日志系统。"""
    settings = get_settings().logging

    level = getattr(logging, settings.level.upper(), logging.DEBUG)
    root_logger = logging.getLogger("loseweight")
    root_logger.setLevel(level)

    # 避免重复添加 handler
    if root_logger.handlers:
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    if settings.enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 文件输出
    if settings.enable_file:
        log_dir = Path(settings.dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            log_dir / "app.log", encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    root_logger.info("日志系统初始化完成 (level=%s)", settings.level)
