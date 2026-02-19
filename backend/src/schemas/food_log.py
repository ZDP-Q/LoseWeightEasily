from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class FoodLogBase(BaseModel):
    food_name: str
    calories: float
    timestamp: Optional[datetime] = None

class FoodLogCreate(FoodLogBase):
    pass

class FoodLogRead(FoodLogBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True
