from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WeightCreate(BaseModel):
    weight_kg: float
    notes: Optional[str] = ""


class WeightRead(BaseModel):
    id: int
    weight_kg: float
    recorded_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True
