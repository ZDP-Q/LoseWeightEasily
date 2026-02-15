from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class WeightCreate(BaseModel):
    weight_kg: float = Field(ge=0.1, le=500, description="体重 (kg)")
    notes: Optional[str] = Field(default="", max_length=200)


class WeightUpdate(BaseModel):
    weight_kg: Optional[float] = Field(default=None, ge=0.1, le=500)
    notes: Optional[str] = Field(default=None, max_length=200)


class WeightRead(BaseModel):
    id: int
    weight_kg: float
    recorded_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True
