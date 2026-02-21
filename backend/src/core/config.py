from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
)


class DatabaseSettings(BaseModel):
    url: str = Field(
        default="postgresql://user_ZWm5Eb:password_PprMP3@localhost:5432/loss_weight"
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


class MinIOSettings(BaseModel):
    endpoint: str = Field(default="localhost:19000")
    access_key: str = Field(default="minio_jPwDBK")
    secret_key: str = Field(default="minio_8kh4Jf")
    secure: bool = Field(default=False)
    bucket_name: str = Field(default="food-recognition")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LOSS_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    milvus: MilvusSettings = Field(default_factory=MilvusSettings)
    minio: MinIOSettings = Field(default_factory=MinIOSettings)
    embedding: EmbeddingModelSettings = Field(default_factory=EmbeddingModelSettings)
    search: SearchSettings = Field(default_factory=SearchSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            YamlConfigSettingsSource(settings_cls),
        )


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    """
    A simple custom settings source that loads variables from a YAML file
    at the root of the project.
    """

    def get_field_value(self, field_name: str, field: Any) -> tuple[Any, str, bool]:
        # Nothing to do here for this simple source
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        config_file = Path("config.yaml")
        if not config_file.exists():
            # Try looking in parent directory (backend/config.yaml)
            config_file = Path(__file__).parent.parent.parent / "config.yaml"

        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                return {}
        return {}


@lru_cache
def get_settings() -> Settings:
    # Environment variables (LOSS_*) override YAML, which override defaults.
    return Settings()
