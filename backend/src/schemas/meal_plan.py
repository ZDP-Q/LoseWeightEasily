from pydantic import BaseModel, Field
from typing import List, Optional


class MealPlanRequest(BaseModel):
    ingredients: List[str] = Field(min_length=1, max_length=20)
    preferences: Optional[str] = Field(default="", max_length=500)
    dietary_restrictions: Optional[str] = Field(default="", max_length=500)


class MealPlanResponse(BaseModel):
    plan: str
    ingredients: List[str]
