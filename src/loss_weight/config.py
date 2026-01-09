"""
配置管理模块

使用 Pydantic Settings 管理所有配置项，支持环境变量和 YAML 配置文件。
优先级：环境变量 > YAML 配置文件 > 默认值
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _load_yaml_config() -> dict[str, Any]:
    """加载 YAML 配置文件"""
    config_file = Path("config.yaml")
    if config_file.exists():
        try:
            # 懒加载 yaml
            import yaml

            with open(config_file, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    return {}


# 预加载 YAML 配置
_yaml_config = _load_yaml_config()


class DatabaseSettings(BaseModel):
    """数据库配置"""

    path: str = Field(default="food_data.db", description="数据库文件路径")


class DataSettings(BaseModel):
    """数据文件配置"""

    dir: str = Field(default="data", description="数据目录")
    json_file: str = Field(
        default="FoodData_Central_foundation_food_json_2025-12-18.json",
        description="JSON 数据文件名",
    )

    @property
    def json_path(self) -> Path:
        """获取 JSON 数据文件的完整路径"""
        return Path(self.dir) / self.json_file


class IndexSettings(BaseModel):
    """索引配置"""

    file: str = Field(default="food_index.faiss", description="FAISS 索引文件路径")
    metadata: str = Field(default="food_metadata.pkl", description="元数据文件路径")


class EmbeddingSettings(BaseModel):
    """嵌入模型配置"""

    model: str = Field(default="paraphrase-multilingual-MiniLM-L12-v2", description="嵌入模型名称")


class SearchSettings(BaseModel):
    """搜索配置"""

    limit: int = Field(default=10, ge=1, le=100, description="默认搜索结果数量")
    threshold: float = Field(default=0.3, ge=0, le=1, description="相似度阈值")


class LLMSettings(BaseModel):
    """LLM API 配置"""

    api_key: str = Field(default="", description="API 密钥")
    base_url: str = Field(default="https://api.openai.com/v1", description="API 基础 URL")
    model: str = Field(default="gpt-3.5-turbo", description="模型名称")

    @property
    def is_configured(self) -> bool:
        """检查 LLM 是否已配置"""
        return bool(self.api_key)


class LoggingSettings(BaseModel):
    """日志配置"""

    mode: Literal["dev", "release"] = Field(default="dev", description="日志模式")
    level: str = Field(default="DEBUG", description="日志级别")
    dir: str = Field(default="logs", description="日志文件目录")
    enable_console: bool = Field(default=True, description="是否启用控制台输出")
    enable_file: bool = Field(default=True, description="是否启用文件日志")


class Settings(BaseSettings):
    """
    应用配置类

    支持从环境变量和 YAML 文件加载配置。
    环境变量使用 LOSS_ 前缀。
    """

    model_config = SettingsConfigDict(
        env_prefix="LOSS_", env_nested_delimiter="__", case_sensitive=False, extra="ignore"
    )

    # 嵌套配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    data: DataSettings = Field(default_factory=DataSettings)
    index: IndexSettings = Field(default_factory=IndexSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    search: SearchSettings = Field(default_factory=SearchSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    # 营养素编号 (USDA标准)
    energy_nutrient_number: str = Field(default="208", description="能量营养素编号 (kcal)")

    @model_validator(mode="before")
    @classmethod
    def load_yaml_config(cls, data: dict[str, Any]) -> dict[str, Any]:
        """从 YAML 配置文件加载默认值"""
        # 合并 YAML 配置（YAML 作为默认值，环境变量覆盖）
        merged = {}

        # 首先加载 YAML 配置
        yaml_config = _yaml_config

        # 数据库配置
        if "database" in yaml_config:
            merged["database"] = yaml_config["database"]

        # 数据配置
        if "data" in yaml_config:
            merged["data"] = yaml_config["data"]

        # 索引配置
        if "index" in yaml_config:
            merged["index"] = yaml_config["index"]

        # 嵌入配置
        if "embedding" in yaml_config:
            merged["embedding"] = yaml_config["embedding"]

        # 搜索配置
        if "search" in yaml_config:
            merged["search"] = yaml_config["search"]

        # LLM 配置
        if "llm" in yaml_config:
            merged["llm"] = yaml_config["llm"]

        # 日志配置
        if "logging" in yaml_config:
            merged["logging"] = yaml_config["logging"]

        # 环境变量数据会覆盖（由 pydantic-settings 处理）
        merged.update(data)

        return merged

    # ========== 便捷属性 ==========

    @property
    def DB_PATH(self) -> str:
        """兼容旧代码：数据库路径"""
        return self.database.path

    @property
    def DATA_DIR(self) -> Path:
        """兼容旧代码：数据目录"""
        return Path(self.data.dir)

    @property
    def JSON_DATA_FILE(self) -> str:
        """兼容旧代码：JSON 数据文件名"""
        return self.data.json_file

    @property
    def INDEX_FILE(self) -> str:
        """兼容旧代码：索引文件路径"""
        return self.index.file

    @property
    def METADATA_FILE(self) -> str:
        """兼容旧代码：元数据文件路径"""
        return self.index.metadata

    @property
    def EMBEDDING_MODEL(self) -> str:
        """兼容旧代码：嵌入模型名称"""
        return self.embedding.model

    @property
    def DEFAULT_SEARCH_LIMIT(self) -> int:
        """兼容旧代码：默认搜索限制"""
        return self.search.limit

    @property
    def SIMILARITY_THRESHOLD(self) -> float:
        """兼容旧代码：相似度阈值"""
        return self.search.threshold

    @property
    def ENERGY_NUTRIENT_NUMBER(self) -> str:
        """兼容旧代码：能量营养素编号"""
        return self.energy_nutrient_number

    @property
    def LLM_API_KEY(self) -> str:
        """兼容旧代码：LLM API 密钥"""
        return self.llm.api_key

    @property
    def LLM_BASE_URL(self) -> str:
        """兼容旧代码：LLM API 基础 URL"""
        return self.llm.base_url

    @property
    def LLM_MODEL(self) -> str:
        """兼容旧代码：LLM 模型名称"""
        return self.llm.model

    # ========== 实用方法 ==========

    def get_json_data_path(self) -> Path:
        """获取 JSON 数据文件的完整路径"""
        return self.data.json_path

    def database_exists(self) -> bool:
        """检查数据库文件是否存在"""
        return Path(self.database.path).exists()

    def index_exists(self) -> bool:
        """检查 FAISS 索引文件是否存在"""
        return Path(self.index.file).exists() and Path(self.index.metadata).exists()

    def get_config_source(self, config_name: str) -> Literal["env", "yaml", "default"]:
        """
        获取配置来源

        Args:
            config_name: 配置名称（如 'LLM_API_KEY'）

        Returns:
            配置来源：'env' | 'yaml' | 'default'
        """
        import os

        env_map = {
            "LLM_API_KEY": ("LOSS_LLM_API_KEY", ["llm", "api_key"]),
            "LLM_BASE_URL": ("LOSS_LLM_BASE_URL", ["llm", "base_url"]),
            "LLM_MODEL": ("LOSS_LLM_MODEL", ["llm", "model"]),
        }

        if config_name not in env_map:
            return "default"

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


@lru_cache
def get_settings() -> Settings:
    """
    获取配置单例

    使用 lru_cache 确保配置只加载一次。
    """
    return Settings()


# 兼容旧代码的别名
config = get_settings()


class Config:
    """
    旧配置类（兼容层）

    @deprecated 请使用 get_settings() 或 Settings 类
    """

    def __getattr__(self, name: str) -> Any:
        return getattr(get_settings(), name)

    def __class_getitem__(cls, name: str) -> Any:
        return getattr(get_settings(), name)

    @classmethod
    def get_json_data_path(cls) -> Path:
        return get_settings().get_json_data_path()

    @classmethod
    def database_exists(cls) -> bool:
        return get_settings().database_exists()

    @classmethod
    def index_exists(cls) -> bool:
        return get_settings().index_exists()

    @classmethod
    def get_config_source(cls, config_name: str) -> str:
        return get_settings().get_config_source(config_name)
