"""
Pydantic 数据模型

定义所有核心数据结构，确保数据验证和类型安全。
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ============================================================================
# 食物相关模型
# ============================================================================


class Nutrient(BaseModel):
    """营养素模型"""

    model_config = ConfigDict(from_attributes=True)

    nutrient_id: int = Field(..., description="营养素ID")
    nutrient_number: str | None = Field(None, description="营养素编号")
    nutrient_name: str | None = Field(None, description="营养素名称")
    unit_name: str | None = Field(None, description="单位名称")
    rank: int | None = Field(None, description="排序")


class FoodNutrient(BaseModel):
    """食品营养素关联模型"""

    model_config = ConfigDict(from_attributes=True)

    fdc_id: int = Field(..., description="食品ID")
    nutrient_id: int = Field(..., description="营养素ID")
    amount: float | None = Field(None, ge=0, description="含量")
    data_points: int | None = Field(None, description="数据点数量")
    min_value: float | None = Field(None, description="最小值")
    max_value: float | None = Field(None, description="最大值")
    median_value: float | None = Field(None, description="中位数")


class FoodPortion(BaseModel):
    """食品份量模型"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="份量ID")
    fdc_id: int = Field(..., description="食品ID")
    amount: float | None = Field(None, ge=0, description="数量")
    measure_unit_name: str | None = Field(None, description="计量单位名称")
    measure_unit_abbreviation: str | None = Field(None, description="计量单位缩写")
    gram_weight: float | None = Field(None, ge=0, description="克重")
    modifier: str | None = Field(None, description="修饰符")
    sequence_number: int | None = Field(None, description="序号")


class Food(BaseModel):
    """食品基本信息模型"""

    model_config = ConfigDict(from_attributes=True)

    fdc_id: int = Field(..., description="食品数据中心ID")
    food_class: str | None = Field(None, description="食品类别")
    description: str = Field(..., description="食品描述")
    data_type: str | None = Field(None, description="数据类型")
    ndb_number: int | None = Field(None, description="NDB编号")
    publication_date: str | None = Field(None, description="发布日期")
    food_category: str | None = Field(None, description="食品分类")
    scientific_name: str | None = Field(None, description="学名")


class FoodSearchResult(BaseModel):
    """食物搜索结果模型"""

    model_config = ConfigDict(from_attributes=True)

    fdc_id: int = Field(..., description="食品ID")
    description: str = Field(..., description="食品描述")
    category: str | None = Field(None, description="食品分类")
    similarity: float = Field(..., ge=0, le=1, description="相似度分数")


class FoodCompleteInfo(BaseModel):
    """食品完整信息模型"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="食品名称")
    category: str | None = Field(None, description="食品分类")
    calories_per_100g: float | None = Field(None, ge=0, description="每100克热量")
    unit: str | None = Field(None, description="单位")
    portions: list[tuple[float, str, float]] = Field(default_factory=list, description="份量信息")
    similarity: float | None = Field(None, ge=0, le=1, description="相似度（搜索时）")


# ============================================================================
# 体重记录相关模型
# ============================================================================


class WeightRecord(BaseModel):
    """体重记录模型"""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(None, description="记录ID")
    weight_kg: float = Field(..., gt=0, le=500, description="体重（千克）")
    recorded_at: datetime | str | None = Field(None, description="记录时间")
    notes: str = Field(default="", max_length=500, description="备注")


class WeightRecordCreate(BaseModel):
    """创建体重记录的输入模型"""

    weight_kg: float = Field(..., gt=0, le=500, description="体重（千克）")
    notes: str = Field(default="", max_length=500, description="备注")

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("体重必须大于 0")
        if v > 500:
            raise ValueError("体重数值不合理")
        return round(v, 2)


class WeightStatistics(BaseModel):
    """体重统计模型"""

    total_records: int = Field(default=0, ge=0, description="总记录数")
    latest_weight: float | None = Field(None, description="最新体重")
    latest_date: str | None = Field(None, description="最新记录日期")
    earliest_weight: float | None = Field(None, description="最早体重")
    earliest_date: str | None = Field(None, description="最早记录日期")
    weight_change: float | None = Field(None, description="体重变化")
    average_weight: float | None = Field(None, description="平均体重")
    min_weight: float | None = Field(None, description="最低体重")
    max_weight: float | None = Field(None, description="最高体重")


# ============================================================================
# BMR / TDEE 相关模型
# ============================================================================

Gender = Literal["male", "female"]
ActivityLevel = Literal["sedentary", "light", "moderate", "active", "very_active"]


class BMRInput(BaseModel):
    """BMR 计算输入模型"""

    weight_kg: float = Field(..., gt=0, le=500, description="体重（千克）")
    height_cm: float = Field(..., gt=50, le=300, description="身高（厘米）")
    age: int = Field(..., gt=0, le=150, description="年龄")
    gender: Gender = Field(..., description="性别")

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        if v <= 0 or v > 500:
            raise ValueError("体重必须在 0-500 kg 之间")
        return v

    @field_validator("height_cm")
    @classmethod
    def validate_height(cls, v: float) -> float:
        if v <= 50 or v > 300:
            raise ValueError("身高必须在 50-300 cm 之间")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v <= 0 or v > 150:
            raise ValueError("年龄必须在 1-150 岁之间")
        return v


class BMRResult(BaseModel):
    """BMR 计算结果模型"""

    bmr: float = Field(..., description="基础代谢率 (kcal/day)")
    input_data: BMRInput = Field(..., description="输入数据")


class TDEEResult(BaseModel):
    """TDEE 计算结果模型"""

    bmr: float = Field(..., description="基础代谢率")
    activity_level: ActivityLevel = Field(..., description="活动水平")
    tdee: float = Field(..., description="每日总能量消耗 (kcal/day)")
    multiplier: float = Field(..., description="活动系数")


# ============================================================================
# 餐食规划相关模型
# ============================================================================


class MealPlanRequest(BaseModel):
    """餐食规划请求模型"""

    ingredients: list[str] = Field(..., min_length=1, description="食材列表")
    preferences: str = Field(default="", description="饮食偏好")
    dietary_restrictions: str = Field(default="", description="饮食限制")

    @field_validator("ingredients")
    @classmethod
    def validate_ingredients(cls, v: list[str]) -> list[str]:
        # 过滤空字符串
        cleaned = [item.strip() for item in v if item.strip()]
        if not cleaned:
            raise ValueError("至少需要提供一种食材")
        return cleaned


class MealPlanResponse(BaseModel):
    """餐食规划响应模型"""

    ingredients: list[str] = Field(..., description="使用的食材")
    plan: str = Field(..., description="生成的餐食计划")
    model_used: str = Field(..., description="使用的模型")


# ============================================================================
# 数据库统计模型
# ============================================================================


class DatabaseStatistics(BaseModel):
    """数据库统计信息模型"""

    foods: int = Field(default=0, ge=0, description="食品数量")
    nutrients: int = Field(default=0, ge=0, description="营养素种类")
    food_nutrients: int = Field(default=0, ge=0, description="食品-营养素关联")
    portions: int = Field(default=0, ge=0, description="份量数据")


# ============================================================================
# 搜索相关模型
# ============================================================================


class SearchQuery(BaseModel):
    """搜索查询模型"""

    query: str = Field(..., min_length=1, max_length=200, description="搜索关键词")
    limit: int = Field(default=10, gt=0, le=100, description="结果数量限制")
    threshold: float = Field(default=0.3, ge=0, le=1, description="相似度阈值")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("搜索关键词不能为空")
        return cleaned
