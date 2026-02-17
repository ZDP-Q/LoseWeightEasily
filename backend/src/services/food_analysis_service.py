import logging

from ..schemas.food_analysis import FoodAnalysisResult, FoodRecognitionResponse

logger = logging.getLogger("loseweight.food_analysis")


class FoodAnalysisService:
    """食物分析服务，委托给 LoseWeightAgent 的 FoodAnalyzer（三路并发）。"""

    def __init__(self, agent):
        self.agent = agent

    async def analyze_food_image(self, image_data: bytes) -> FoodRecognitionResponse:
        if not self.agent:
            raise Exception("AI Agent 未初始化")

        result = await self.agent.analyze_food_bytes(image_data)

        if isinstance(result, dict) and "error" in result:
            raise Exception(result["error"])

        # 将 Agent 的 FoodRecognitionResponse 转为后端的 schema
        return FoodRecognitionResponse(
            final_food_name=result.final_food_name,
            final_estimated_calories=result.final_estimated_calories,
            raw_data=[
                FoodAnalysisResult(
                    food_name=r.food_name,
                    calories=r.calories,
                    confidence=r.confidence,
                    components=r.components,
                )
                for r in result.raw_data
            ],
            timestamp=result.timestamp,
        )
