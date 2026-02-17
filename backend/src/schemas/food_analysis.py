from pydantic import BaseModel, Field, ConfigDict
from typing import List


class FoodAnalysisResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    food_name: str = Field(..., alias="food_name")
    calories: int = Field(..., alias="estimated_calories")
    confidence: float = Field(default=0.0)
    components: List[str] = Field(default_factory=list)


class FoodRecognitionResponse(BaseModel):
    final_food_name: str
    final_estimated_calories: int
    raw_data: List[FoodAnalysisResult]
    timestamp: str
