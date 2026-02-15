from pydantic import BaseModel
from typing import Optional


class FoodSearchResult(BaseModel):
    fdc_id: int
    description: str
    category: Optional[str] = None
    calories_per_100g: Optional[float] = None
    similarity: float
