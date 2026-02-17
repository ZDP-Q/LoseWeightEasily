import logging
from typing import List, Optional

from ..schemas.meal_plan import MealPlanResponse, MealPlanError

logger = logging.getLogger("loseweight.meal_planner")

# 食材/偏好输入的最大长度限制
MAX_INGREDIENTS = 20


class MealPlannerService:
    """饮食规划服务，委托给 LoseWeightAgent 的 MealPlanner。"""

    def __init__(self, agent):
        self.agent = agent

    async def generate_plan(
        self,
        ingredients: List[str],
        preferences: str = "",
        restrictions: str = "",
        goal: str = "lose_weight",
        target_calories: Optional[int] = None,
    ) -> MealPlanResponse:
        if not self.agent:
            raise MealPlanError(
                "AI Agent 未初始化。请检查 config.yaml 中的 LLM API 配置。",
                status_code=503,
            )

        # 输入长度校验
        if len(ingredients) > MAX_INGREDIENTS:
            raise MealPlanError(
                f"食材数量不能超过 {MAX_INGREDIENTS} 种。", status_code=422
            )

        try:
            result = await self.agent.plan_meals_direct(
                ingredients=ingredients,
                target_calories=target_calories or 1800,
                goal=goal,
            )

            if not result:
                raise MealPlanError(
                    "AI 响应格式错误，无法解析为食谱。", status_code=500
                )

            # 将 Agent 的 DailyMealPlan 转换为后端的 MealPlanResponse
            return MealPlanResponse.model_validate(result.model_dump())

        except MealPlanError:
            raise
        except Exception as e:
            logger.exception("生成食谱时发生未知错误")
            raise MealPlanError(f"生成计划时出错: {str(e)}", status_code=500)
