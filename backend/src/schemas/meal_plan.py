from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict


class MealPlanRequest(BaseModel):
    ingredients: List[str] = Field(min_length=1, max_length=20)
    preferences: Optional[str] = Field(default="", max_length=500)
    dietary_restrictions: Optional[str] = Field(default="", max_length=500)
    goal: Optional[str] = Field(default="lose_weight", description="lose_weight or maintain")
    target_calories: Optional[int] = None


class MealDetail(BaseModel):
    name: str = Field(..., description="菜品名称")
    calories: int = Field(..., description="卡路里")
    ingredients_used: List[str] = Field(default_factory=list, description="使用的食材")
    instructions: str = Field("", description="简短做法")


class DailySummary(BaseModel):
    target_calories: int
    total_protein: Optional[str] = None
    total_carbs: Optional[str] = None
    total_fat: Optional[str] = None


class MealPlanResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    daily_summary: DailySummary
    meals: Dict[str, MealDetail]
    tips: List[str] = Field(default_factory=list)


class MealPlanError(Exception):
    """食谱规划业务异常。"""

    def __init__(self, message: str, *, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

