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

    # 定义日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handlers = []

    # 控制台输出处理器
    if settings.enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    # 文件输出处理器
    if settings.enable_file:
        log_dir = Path(settings.dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清理现有的 handler 避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    for handler in handlers:
        root_logger.addHandler(handler)

    # 专门处理 uvicorn 的日志器，确保它们不使用自己的默认格式
    uvicorn_loggers = ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]
    for logger_name in uvicorn_loggers:
        u_logger = logging.getLogger(logger_name)
        u_logger.handlers = []  # 清空 uvicorn 默认的 handlers
        u_logger.propagate = True  # 让日志流向根日志器

    logging.getLogger("loseweight").info(
        "日志系统初始化完成 (level=%s, file=%s)", settings.level, settings.enable_file
    )
