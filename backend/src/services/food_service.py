"""食物搜索服务，基于 Milvus 向量数据库。"""


from LoseWeightAgent.src.services.food_search import FoodSearchService
from LoseWeightAgent.src.schemas import FoodNutritionSearchResult


class FoodService:
    """食物搜索服务（代理到 LoseWeightAgent 的 FoodSearchService）。"""

    def __init__(self, food_search: FoodSearchService):
        self.food_search = food_search

    def search_by_text(
        self, query: str, limit: int = 10
    ) -> list[FoodNutritionSearchResult]:
        """通过文本搜索食物。"""
        return self.food_search.search_by_text(query, limit)

    def search_by_image(
        self,
        image_data: bytes,
        limit: int = 10,
        image_format: str = "jpeg",
    ) -> list[FoodNutritionSearchResult]:
        """通过图片搜索食物。"""
        return self.food_search.search_by_image(image_data, limit, image_format)
