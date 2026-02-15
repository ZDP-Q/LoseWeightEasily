import openai
from typing import List
from ..core.config import get_settings


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
            return "LLM API 未配置。请在 config.yaml 中添加 API 密钥。"

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
        except Exception as e:
            return f"生成计划时出错: {str(e)}"
