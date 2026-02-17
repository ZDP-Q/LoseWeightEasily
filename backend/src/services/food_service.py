import faiss
from typing import List
from sentence_transformers import SentenceTransformer

from ..repositories.food_repository import FoodRepository
from ..schemas.food import FoodSearchResult


class FoodService:
    def __init__(
        self,
        repository: FoodRepository,
        model: SentenceTransformer,
        index: faiss.Index,
        metadata: List[int],
    ):
        self.repo = repository
        self.model = model
        self.index = index
        self.metadata = metadata

    def search_foods(self, query: str, limit: int = 10) -> List[FoodSearchResult]:
        if self.index is None:
            return []

        query_vector = self.model.encode([query]).astype("float32")
        distances, indices = self.index.search(query_vector, limit)

        # 批量收集所有有效的 fdc_id，避免 N+1 查询
        # metadata 可能包含 int (fdc_id) 或 dict {"fdc_id": ..., "description": ...}
        valid_entries: list[tuple[float, int]] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.metadata):
                entry = self.metadata[idx]
                fdc_id = entry["fdc_id"] if isinstance(entry, dict) else entry
                valid_entries.append((float(dist), fdc_id))

        if not valid_entries:
            return []

        # 一次性批量查询所有食物详情
        fdc_ids = [fdc_id for _, fdc_id in valid_entries]
        details_map = self.repo.get_foods_simple_details(fdc_ids)

        results = []
        for dist, fdc_id in valid_entries:
            detail = details_map.get(fdc_id)
            if detail:
                results.append(
                    FoodSearchResult(
                        fdc_id=fdc_id,
                        description=detail["description"],
                        category=detail["category"],
                        calories_per_100g=detail["calories_per_100g"],
                        similarity=1 - dist,
                    )
                )

        return results
