"""
配置管理模块

集中管理所有配置项，支持环境变量和 YAML 配置文件。
优先级：环境变量 > YAML 配置文件 > 默认值
"""

import os
from pathlib import Path
from typing import Any

import yaml


def _load_yaml_config() -> dict[str, Any]:
    """加载 YAML 配置文件"""
    config_file = Path("config.yaml")
    if config_file.exists():
        try:
            with open(config_file, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    return {}


# 加载 YAML 配置
_yaml_config = _load_yaml_config()


def _get_config(env_key: str, yaml_path: list[str], default: Any = "") -> Any:
    """
    获取配置值

    Args:
        env_key: 环境变量键名
        yaml_path: YAML 配置路径（如 ['llm', 'api_key']）
        default: 默认值

    Returns:
        配置值（优先级：环境变量 > YAML > 默认值）
    """
    # 1. 先尝试环境变量
    env_value = os.getenv(env_key)
    if env_value is not None:
        return env_value

    # 2. 尝试从 YAML 读取
    value = _yaml_config
    for key in yaml_path:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            value = None
            break

    if value is not None:
        return value

    # 3. 返回默认值
    return default


class Config:
    """应用配置类"""

    # 数据库配置
    DB_PATH: str = _get_config("LOSS_DB_PATH", ["database", "path"], "food_data.db")

    # 数据文件路径
    DATA_DIR: Path = Path(_get_config("LOSS_DATA_DIR", ["data", "dir"], "data"))
    JSON_DATA_FILE: str = "FoodData_Central_foundation_food_json_2025-12-18.json"

    # FAISS 索引配置
    INDEX_FILE: str = _get_config("LOSS_INDEX_FILE", ["index", "file"], "food_index.faiss")
    METADATA_FILE: str = _get_config("LOSS_METADATA_FILE", ["index", "metadata"], "food_metadata.pkl")

    # 嵌入模型配置
    EMBEDDING_MODEL: str = _get_config(
        "LOSS_EMBEDDING_MODEL",
        ["embedding", "model"],
        "paraphrase-multilingual-MiniLM-L12-v2"
    )

    # 搜索配置
    DEFAULT_SEARCH_LIMIT: int = int(_get_config("LOSS_SEARCH_LIMIT", ["search", "limit"], "10"))
    SIMILARITY_THRESHOLD: float = float(_get_config("LOSS_SIMILARITY_THRESHOLD", ["search", "threshold"], "0.3"))

    # 营养素编号 (USDA标准)
    ENERGY_NUTRIENT_NUMBER: str = "208"  # kcal

    # LLM API 配置
    LLM_API_KEY: str = _get_config("LOSS_LLM_API_KEY", ["llm", "api_key"], "")
    LLM_BASE_URL: str = _get_config("LOSS_LLM_BASE_URL", ["llm", "base_url"], "https://api.openai.com/v1")
    LLM_MODEL: str = _get_config("LOSS_LLM_MODEL", ["llm", "model"], "gpt-3.5-turbo")

    @classmethod
    def get_json_data_path(cls) -> Path:
        """获取 JSON 数据文件的完整路径"""
        return cls.DATA_DIR / cls.JSON_DATA_FILE

    @classmethod
    def database_exists(cls) -> bool:
        """检查数据库文件是否存在"""
        return Path(cls.DB_PATH).exists()

    @classmethod
    def index_exists(cls) -> bool:
        """检查 FAISS 索引文件是否存在"""
        return Path(cls.INDEX_FILE).exists() and Path(cls.METADATA_FILE).exists()

    @classmethod
    def get_config_source(cls, config_name: str) -> str:
        """
        获取配置来源

        Args:
            config_name: 配置名称（如 'LLM_API_KEY'）

        Returns:
            配置来源：'env' | 'yaml' | 'default'
        """
        env_map = {
            "LLM_API_KEY": ("LOSS_LLM_API_KEY", ["llm", "api_key"]),
            "LLM_BASE_URL": ("LOSS_LLM_BASE_URL", ["llm", "base_url"]),
            "LLM_MODEL": ("LOSS_LLM_MODEL", ["llm", "model"]),
        }

        if config_name not in env_map:
            return "unknown"

        env_key, yaml_path = env_map[config_name]

        # 检查环境变量
        if os.getenv(env_key):
            return "env"

        # 检查 YAML
        value = _yaml_config
        for key in yaml_path:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = None
                break

        if value:
            return "yaml"

        return "default"


# 默认配置实例
config = Config()
