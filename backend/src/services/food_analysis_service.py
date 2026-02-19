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

        if result is None:
            raise Exception("AI 服务未返回结果，请检查后端日志")

        if isinstance(result, dict) and "error" in result:
            raise Exception(result["error"])

        # 处理返回结果是字典的情况（防止 AttributeError）
        if isinstance(result, dict):
            return FoodRecognitionResponse(
                final_food_name=result.get("final_food_name", "未知食物"),
                final_estimated_calories=result.get("final_estimated_calories", 0),
                raw_data=[
                    FoodAnalysisResult(
                        food_name=r.get("food_name", "未知") if isinstance(r, dict) else getattr(r, "food_name", "未知"),
                        calories=r.get("calories", 0) if isinstance(r, dict) else getattr(r, "calories", 0),
                        confidence=r.get("confidence", 0.0) if isinstance(r, dict) else getattr(r, "confidence", 0.0),
                        components=r.get("components", []) if isinstance(r, dict) else getattr(r, "components", []),
                    )
                    for r in result.get("raw_data", [])
                ],
                timestamp=result.get("timestamp", ""),
            )

        # 将 Agent 的 FoodRecognitionResponse 对象转为后端的 schema
        try:
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
        except AttributeError as e:
            logger.error(f"解析 Agent 返回对象失败: {e}, result type: {type(result)}")
            raise Exception(f"识别结果解析失败: {e}")
