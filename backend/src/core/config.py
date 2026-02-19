from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _load_yaml_config() -> dict[str, Any]:
    # 查找顺序：当前目录 -> 父目录（兼容 src/core 运行）
    config_file = Path("config.yaml")
    if not config_file.exists():
        config_file = Path(__file__).parent.parent.parent / "config.yaml"

    if config_file.exists():
        try:
            with open(config_file, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    return {}


_yaml_config = _load_yaml_config()


class DatabaseSettings(BaseModel):
    url: str = Field(
        default="postgresql://postgres:password@localhost:5432/loss_weight"
    )


class MilvusSettings(BaseModel):
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=19530)
    collection: str = Field(default="usda_foods")


class EmbeddingModelSettings(BaseModel):
    model: str = Field(default="qwen3-vl-embedding")
    dimension: int = Field(default=1024)


class SearchSettings(BaseModel):
    limit: int = Field(default=10)


class LLMSettings(BaseModel):
    api_key: str = Field(default="")
    base_url: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1")
    model: str = Field(default="qwen3.5-plus")


class SecuritySettings(BaseModel):
    api_key: str = Field(default="")
    cors_origins: list[str] = Field(default=["*"])


class LoggingSettings(BaseModel):
    mode: Literal["dev", "release"] = Field(default="dev")
    level: str = Field(default="DEBUG")
    dir: str = Field(default="logs")
    enable_console: bool = Field(default=True)
    enable_file: bool = Field(default=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LOSS_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    milvus: MilvusSettings = Field(default_factory=MilvusSettings)
    embedding: EmbeddingModelSettings = Field(default_factory=EmbeddingModelSettings)
    search: SearchSettings = Field(default_factory=SearchSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    @classmethod
    def from_yaml(cls):
        return cls(**_yaml_config)


@lru_cache
def get_settings() -> Settings:
    return Settings.from_yaml()
