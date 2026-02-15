from pydantic import BaseModel
from typing import Dict


class BMRInput(BaseModel):
    weight_kg: float
    height_cm: float
    age: int
    gender: str  # male/female


class BMRResult(BaseModel):
    bmr: float
    tdee: Dict[str, float]
