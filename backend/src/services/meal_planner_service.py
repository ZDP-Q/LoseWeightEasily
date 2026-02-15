import logging
from typing import List

import openai

from ..core.config import get_settings

logger = logging.getLogger("loseweight.meal_planner")

# 食材/偏好输入的最大长度限制
MAX_INGREDIENTS = 20
MAX_TEXT_LENGTH = 500


class MealPlanError(Exception):
    """食谱规划业务异常。"""

    def __init__(self, message: str, *, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class MealPlannerService:
    def __init__(self):
        self.settings = get_settings().llm
        if self.settings.api_key:
            self.client = openai.AsyncOpenAI(
                api_key=self.settings.api_key, base_url=self.settings.base_url
            )
        else:
            self.client = None

    async def generate_plan(
        self, ingredients: List[str], preferences: str = "", restrictions: str = ""
    ) -> str:
        if not self.client:
            raise MealPlanError(
                "LLM API 未配置。请在 config.yaml 中添加 API 密钥。",
                status_code=503,
            )

        # 输入长度校验
        if len(ingredients) > MAX_INGREDIENTS:
            raise MealPlanError(
                f"食材数量不能超过 {MAX_INGREDIENTS} 种。", status_code=422
            )
        if len(preferences) > MAX_TEXT_LENGTH:
            raise MealPlanError(
                f"偏好描述不能超过 {MAX_TEXT_LENGTH} 个字符。", status_code=422
            )
        if len(restrictions) > MAX_TEXT_LENGTH:
            raise MealPlanError(
                f"饮食限制描述不能超过 {MAX_TEXT_LENGTH} 个字符。", status_code=422
            )

        prompt = f"""
        作为一名营养师，请使用以下主要成分制定一份平衡的一日三餐（早餐、午餐、晚餐）计划：
        食材：{", ".join(ingredients)}
        偏好：{preferences}
        禁忌/限制：{restrictions}
        
        请以清晰、诱人的格式提供计划，并附带热量预估（使用中文）。
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.settings.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except openai.AuthenticationError as e:
            logger.error("LLM API 认证失败: %s", e)
            raise MealPlanError(
                "API 认证失败，请检查 config.yaml 中的 api_key 配置。",
                status_code=401,
            ) from e
        except openai.RateLimitError as e:
            logger.warning("LLM API 请求频率超限: %s", e)
            raise MealPlanError(
                "API 请求频率超限，请稍后再试。", status_code=429
            ) from e
        except openai.APITimeoutError as e:
            logger.warning("LLM API 响应超时: %s", e)
            raise MealPlanError(
                "AI 响应超时，请稍后再试。", status_code=504
            ) from e
        except openai.BadRequestError as e:
            logger.error("LLM API 请求参数错误: %s", e)
            raise MealPlanError(
                f"请求参数错误: {e.message}", status_code=400
            ) from e
        except openai.APIConnectionError as e:
            logger.error("无法连接到 LLM API: %s", e)
            raise MealPlanError(
                "无法连接到 AI 服务，请检查网络或 base_url 配置。",
                status_code=502,
            ) from e
        except Exception as e:
            logger.exception("生成食谱时发生未知错误")
            raise MealPlanError(
                f"生成计划时出错: {type(e).__name__}: {e}", status_code=500
            ) from e
