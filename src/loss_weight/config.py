"""
配置管理模块

集中管理所有配置项，支持环境变量覆盖。
"""

import os
from pathlib import Path


class Config:
    """应用配置类"""
    
    # 数据库配置
    DB_PATH: str = os.getenv("LOSS_DB_PATH", "food_data.db")
    
    # 数据文件路径
    DATA_DIR: Path = Path(os.getenv("LOSS_DATA_DIR", "data"))
    JSON_DATA_FILE: str = "FoodData_Central_foundation_food_json_2025-12-18.json"
    
    # FAISS 索引配置
    INDEX_FILE: str = os.getenv("LOSS_INDEX_FILE", "food_index.faiss")
    METADATA_FILE: str = os.getenv("LOSS_METADATA_FILE", "food_metadata.pkl")
    
    # 嵌入模型配置
    EMBEDDING_MODEL: str = os.getenv(
        "LOSS_EMBEDDING_MODEL",
        "paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    # 搜索配置
    DEFAULT_SEARCH_LIMIT: int = int(os.getenv("LOSS_SEARCH_LIMIT", "10"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("LOSS_SIMILARITY_THRESHOLD", "0.3"))
    
    # 营养素编号 (USDA标准)
    ENERGY_NUTRIENT_NUMBER: str = "208"  # kcal
    
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


# 默认配置实例
config = Config()
