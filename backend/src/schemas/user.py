from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    name: str
    age: int
    gender: str
    height_cm: float
    initial_weight_kg: float
    target_weight_kg: float
    bmr: Optional[float] = None
    daily_calorie_goal: Optional[float] = None


class UserRead(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    height_cm: float
    initial_weight_kg: float
    target_weight_kg: float
    bmr: Optional[float] = None
    daily_calorie_goal: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    initial_weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    bmr: Optional[float] = None
    daily_calorie_goal: Optional[float] = None
