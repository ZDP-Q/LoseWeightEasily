from pydantic import BaseModel
from typing import List, Optional


class MealPlanRequest(BaseModel):
    ingredients: List[str]
    preferences: Optional[str] = ""
    dietary_restrictions: Optional[str] = ""


class MealPlanResponse(BaseModel):
    plan: str
    ingredients: List[str]
