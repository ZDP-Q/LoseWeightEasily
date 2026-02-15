from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=1, le=150)
    gender: str = Field(pattern=r"^(male|female)$")
    height_cm: float = Field(ge=50, le=300)
    initial_weight_kg: float = Field(ge=10, le=500)
    target_weight_kg: float = Field(ge=10, le=500)
    bmr: Optional[float] = None
    daily_calorie_goal: Optional[float] = Field(default=None, ge=500, le=10000)


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
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    age: Optional[int] = Field(default=None, ge=1, le=150)
    gender: Optional[str] = Field(default=None, pattern=r"^(male|female)$")
    height_cm: Optional[float] = Field(default=None, ge=50, le=300)
    initial_weight_kg: Optional[float] = Field(default=None, ge=10, le=500)
    target_weight_kg: Optional[float] = Field(default=None, ge=10, le=500)
    bmr: Optional[float] = None
    daily_calorie_goal: Optional[float] = Field(default=None, ge=500, le=10000)
