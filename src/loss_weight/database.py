"""
数据库管理模块

负责 SQLite 数据库的创建、数据导入和查询操作。
使用 Pydantic 模型确保数据类型安全。
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .models import (
    DatabaseStatistics,
    FoodCompleteInfo,
)

if TYPE_CHECKING:
    import logging

    from .config import Settings


class DatabaseManager:
    """数据库管理器类"""

    def __init__(self, db_path: str | None = None, settings: Settings | None = None):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径，默认使用配置中的路径
            settings: 配置实例
        """
        if db_path is not None:
            self._db_path = db_path
        elif settings is not None:
            self._db_path = settings.database.path
        else:
            # 懒加载配置
            from .config import get_settings

            self._db_path = get_settings().database.path

        self._settings = settings
        self._logger: logging.Logger | None = None

    @property
    def logger(self) -> logging.Logger:
        """懒加载日志记录器"""
        if self._logger is None:
            from .container import get_logger

            self._logger = get_logger(__name__)
        return self._logger

    @property
    def db_path(self) -> str:
        """获取数据库路径"""
        return self._db_path

    @property
    def settings(self) -> Settings:
        """懒加载配置"""
        if self._settings is None:
            from .config import get_settings

            self._settings = get_settings()
        return self._settings

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        获取数据库连接（上下文管理器）

        Yields:
            数据库连接
        """
        conn = sqlite3.connect(self._db_path)
        try:
            yield conn
        finally:
            conn.close()

    def get_raw_connection(self) -> sqlite3.Connection:
        """
        获取原始数据库连接（兼容旧代码）

        注意：调用者需要自行关闭连接

        Returns:
            数据库连接
        """
        return sqlite3.connect(self._db_path)

    def create_tables(self) -> None:
        """创建数据库表结构"""
        self.logger.debug(f"创建数据库表结构: {self._db_path}")
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 创建食品主表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS foods (
                    fdc_id INTEGER PRIMARY KEY,
                    food_class TEXT,
                    description TEXT,
                    data_type TEXT,
                    ndb_number INTEGER,
                    publication_date TEXT,
                    food_category TEXT,
                    scientific_name TEXT
                )
            """)

            # 创建营养素表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nutrients (
                    id INTEGER PRIMARY KEY,
                    nutrient_id INTEGER,
                    nutrient_number TEXT,
                    nutrient_name TEXT,
                    unit_name TEXT,
                    rank INTEGER,
                    UNIQUE(nutrient_id)
                )
            """)

            # 创建食品营养素关联表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS food_nutrients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fdc_id INTEGER,
                    nutrient_id INTEGER,
                    amount REAL,
                    data_points INTEGER,
                    derivation_code TEXT,
                    min_value REAL,
                    max_value REAL,
                    median_value REAL,
                    FOREIGN KEY (fdc_id) REFERENCES foods (fdc_id),
                    FOREIGN KEY (nutrient_id) REFERENCES nutrients (nutrient_id)
                )
            """)

            # 创建食品份量表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS food_portions (
                    id INTEGER PRIMARY KEY,
                    fdc_id INTEGER,
                    amount REAL,
                    measure_unit_name TEXT,
                    measure_unit_abbreviation TEXT,
                    gram_weight REAL,
                    modifier TEXT,
                    sequence_number INTEGER,
                    FOREIGN KEY (fdc_id) REFERENCES foods (fdc_id)
                )
            """)

            # 创建索引以提高查询性能
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_food_nutrients_fdc_id
                ON food_nutrients(fdc_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_food_nutrients_nutrient_id
                ON food_nutrients(nutrient_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_food_portions_fdc_id
                ON food_portions(fdc_id)
            """)

            # 创建体重记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weight_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    weight_kg REAL NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            """)

            # 创建体重记录时间索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_weight_records_date
                ON weight_records(recorded_at)
            """)

            conn.commit()

    def _insert_food(self, cursor: sqlite3.Cursor, food_data: dict[str, Any]) -> None:
        """插入食品数据"""
        food_category = food_data.get("foodCategory", {})

        cursor.execute(
            """
            INSERT OR REPLACE INTO foods
            (fdc_id, food_class, description, data_type, ndb_number,
             publication_date, food_category, scientific_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                food_data.get("fdcId"),
                food_data.get("foodClass"),
                food_data.get("description"),
                food_data.get("dataType"),
                food_data.get("ndbNumber"),
                food_data.get("publicationDate"),
                food_category.get("description") if food_category else None,
                food_data.get("scientificName"),
            ),
        )

    def _insert_nutrient(self, cursor: sqlite3.Cursor, nutrient_data: dict[str, Any]) -> None:
        """插入营养素数据"""
        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO nutrients
                (nutrient_id, nutrient_number, nutrient_name, unit_name, rank)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    nutrient_data.get("id"),
                    nutrient_data.get("number"),
                    nutrient_data.get("name"),
                    nutrient_data.get("unitName"),
                    nutrient_data.get("rank"),
                ),
            )
        except sqlite3.IntegrityError:
            pass  # 营养素已存在

    def _insert_food_nutrient(
        self, cursor: sqlite3.Cursor, fdc_id: int, food_nutrient: dict[str, Any]
    ) -> None:
        """插入食品营养素关联数据"""
        nutrient = food_nutrient.get("nutrient", {})

        # 先插入营养素
        self._insert_nutrient(cursor, nutrient)

        # 插入食品营养素关系
        cursor.execute(
            """
            INSERT INTO food_nutrients
            (fdc_id, nutrient_id, amount, data_points, derivation_code,
             min_value, max_value, median_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                fdc_id,
                nutrient.get("id"),
                food_nutrient.get("amount"),
                food_nutrient.get("dataPoints"),
                food_nutrient.get("foodNutrientDerivation", {}).get("code"),
                food_nutrient.get("min"),
                food_nutrient.get("max"),
                food_nutrient.get("median"),
            ),
        )

    def _insert_food_portions(
        self, cursor: sqlite3.Cursor, fdc_id: int, portions: list[dict[str, Any]]
    ) -> None:
        """插入食品份量数据"""
        for portion in portions:
            measure_unit = portion.get("measureUnit", {})
            cursor.execute(
                """
                INSERT OR REPLACE INTO food_portions
                (id, fdc_id, amount, measure_unit_name, measure_unit_abbreviation,
                 gram_weight, modifier, sequence_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    portion.get("id"),
                    fdc_id,
                    portion.get("amount"),
                    measure_unit.get("name"),
                    measure_unit.get("abbreviation"),
                    portion.get("gramWeight"),
                    portion.get("modifier"),
                    portion.get("sequenceNumber"),
                ),
            )

    def import_from_json(self, json_file_path: str | Path | None = None) -> DatabaseStatistics:
        """
        从 JSON 文件导入数据到数据库

        Args:
            json_file_path: JSON 文件路径，默认使用配置中的路径

        Returns:
            导入统计信息（DatabaseStatistics 模型）
        """
        json_path = Path(json_file_path) if json_file_path else self.settings.get_json_data_path()
        self.logger.info(f"开始导入 JSON 数据: {json_path}")

        # 读取 JSON 文件
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        # 创建数据库表
        self.create_tables()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 获取食品列表
            foundation_foods = data.get("FoundationFoods", [])
            total_foods = len(foundation_foods)

            self.logger.info(f"找到 {total_foods} 个食品条目")

            # 处理每个食品
            for idx, food in enumerate(foundation_foods, 1):
                if idx % 100 == 0:
                    self.logger.debug(f"导入进度: {idx}/{total_foods}")

                fdc_id = food.get("fdcId")

                # 插入食品基本信息
                self._insert_food(cursor, food)

                # 插入营养素信息
                food_nutrients = food.get("foodNutrients", [])
                for nutrient in food_nutrients:
                    self._insert_food_nutrient(cursor, fdc_id, nutrient)

                # 插入食品份量信息
                food_portions = food.get("foodPortions", [])
                if food_portions:
                    self._insert_food_portions(cursor, fdc_id, food_portions)

            conn.commit()

        # 获取统计信息
        stats = self.get_statistics()

        self.logger.info(f"数据导入完成: {stats.foods} 食品, {stats.nutrients} 营养素")
        return stats

    def get_statistics(self) -> DatabaseStatistics:
        """获取数据库统计信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM foods")
            food_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM nutrients")
            nutrient_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM food_nutrients")
            food_nutrient_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM food_portions")
            portion_count = cursor.fetchone()[0]

        return DatabaseStatistics(
            foods=food_count,
            nutrients=nutrient_count,
            food_nutrients=food_nutrient_count,
            portions=portion_count,
        )

    def get_all_foods(self) -> list[tuple[int, str, str]]:
        """获取所有食品信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fdc_id, description, food_category FROM foods")
            return cursor.fetchall()

    def get_food_info(self, fdc_id: int) -> tuple[str, str] | None:
        """获取食品基本信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT description, food_category
                FROM foods
                WHERE fdc_id = ?
            """,
                (fdc_id,),
            )

            return cursor.fetchone()

    def get_food_calories(self, fdc_id: int) -> tuple[float, str] | None:
        """获取食品的卡路里信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT fn.amount, n.unit_name
                FROM food_nutrients fn
                JOIN nutrients n ON fn.nutrient_id = n.nutrient_id
                WHERE fn.fdc_id = ? AND n.nutrient_number = ?
            """,
                (fdc_id, self.settings.ENERGY_NUTRIENT_NUMBER),
            )

            return cursor.fetchone()

    def get_food_portions(self, fdc_id: int, limit: int = 3) -> list[tuple[float, str, float]]:
        """获取食品份量信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT amount, measure_unit_name, gram_weight
                FROM food_portions
                WHERE fdc_id = ?
                ORDER BY sequence_number
                LIMIT ?
            """,
                (fdc_id, limit),
            )

            return cursor.fetchall()

    def get_food_complete_info(self, fdc_id: int) -> FoodCompleteInfo | None:
        """获取食品完整信息（包括基本信息、卡路里和份量）"""
        food_info = self.get_food_info(fdc_id)
        if not food_info:
            return None

        calorie_info = self.get_food_calories(fdc_id)
        portions = self.get_food_portions(fdc_id)

        return FoodCompleteInfo(
            name=food_info[0],
            category=food_info[1],
            calories_per_100g=calorie_info[0] if calorie_info else None,
            unit=calorie_info[1] if calorie_info else None,
            portions=portions,
        )
