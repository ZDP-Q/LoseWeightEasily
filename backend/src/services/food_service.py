import faiss
from typing import List, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
from sqlmodel import Session, select
from ..models import Food
from ..schemas.food import FoodSearchResult
from ..core.config import get_settings

settings = get_settings()


class FoodService:
    def __init__(
        self,
        session: Session,
        model: SentenceTransformer,
        index: faiss.Index,
        metadata: List[int],
    ):
        self.session = session
        self.model = model
        self.index = index
        self.metadata = metadata

    def search_foods(self, query: str, limit: int = 10) -> List[FoodSearchResult]:
        if self.index is None:
            return []

        query_vector = self.model.encode([query]).astype("float32")
        distances, indices = self.index.search(query_vector, limit)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.metadata):
                fdc_id = self.metadata[idx]
                food_details = self.get_food_simple_details(fdc_id)
                if food_details:
                    results.append(
                        FoodSearchResult(
                            fdc_id=fdc_id,
                            description=food_details["description"],
                            category=food_details["category"],
                            calories_per_100g=food_details["calories_per_100g"],
                            similarity=float(1 - dist),
                        )
                    )

        return results

    def get_food_simple_details(self, fdc_id: int) -> Optional[Dict[str, Any]]:
        statement = select(Food).where(Food.fdc_id == fdc_id)
        food = self.session.exec(statement).first()
        if not food:
            return None

        calories = 0
        for fn in food.nutrients:
            # 208 is the typical nutrient number for Energy (kcal)
            if fn.nutrient.nutrient_number == "208":
                calories = fn.amount
                break

        return {
            "fdc_id": food.fdc_id,
            "description": food.description,
            "category": food.food_category,
            "calories_per_100g": calories,
        }
