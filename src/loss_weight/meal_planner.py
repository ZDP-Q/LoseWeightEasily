"""
餐食规划模块

基于食材和营养信息，使用 LLM 生成一日三餐食谱。
使用懒加载模式和 Pydantic 模型。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import FoodCompleteInfo, MealPlanRequest, MealPlanResponse

if TYPE_CHECKING:
    from openai import OpenAI

    from .config import Settings
    from .database import DatabaseManager


class MealPlanner:
    """餐食规划器"""

    def __init__(
        self,
        db_manager: DatabaseManager | None = None,
        db_path: str | None = None,
        settings: Settings | None = None,
    ):
        """
        初始化餐食规划器

        Args:
            db_manager: 数据库管理器实例
            db_path: 数据库路径（兼容旧代码）
            settings: 配置实例
        """
        self._db_manager = db_manager
        self._db_path = db_path
        self._settings = settings
        self._client: OpenAI | None = None

    @property
    def settings(self) -> Settings:
        """懒加载配置"""
        if self._settings is None:
            from .config import get_settings

            self._settings = get_settings()
        return self._settings

    @property
    def db_manager(self) -> DatabaseManager:
        """懒加载数据库管理器"""
        if self._db_manager is None:
            from .database import DatabaseManager

            self._db_manager = DatabaseManager(db_path=self._db_path, settings=self.settings)
        return self._db_manager

    def _get_client(self) -> OpenAI:
        """获取 OpenAI 客户端（懒加载）"""
        if self._client is None:
            # 懒加载 openai
            from openai import OpenAI

            if not self.settings.LLM_API_KEY:
                raise ValueError(
                    "未配置 LLM API Key。请设置环境变量 LOSS_LLM_API_KEY 或在 config.yaml 中配置"
                )
            self._client = OpenAI(
                api_key=self.settings.LLM_API_KEY, base_url=self.settings.LLM_BASE_URL
            )
        return self._client

    def get_ingredient_nutrition(self, ingredient: str) -> FoodCompleteInfo | None:
        """
        获取食材的营养信息

        Args:
            ingredient: 食材名称

        Returns:
            FoodCompleteInfo 模型或 None
        """
        # 通过数据库搜索获取营养信息
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()

            # 简单模糊搜索
            cursor.execute(
                """
                SELECT f.fdc_id, f.description, f.food_category
                FROM foods f
                WHERE f.description LIKE ?
                LIMIT 1
            """,
                (f"%{ingredient}%",),
            )

            result = cursor.fetchone()

        if result:
            fdc_id = result[0]
            return self.db_manager.get_food_complete_info(fdc_id)
        return None

    def generate_meal_plan(
        self,
        request: MealPlanRequest | None = None,
        ingredients: list[str] | None = None,
        preferences: str = "",
        dietary_restrictions: str = "",
    ) -> MealPlanResponse:
        """
        生成一日三餐食谱

        Args:
            request: MealPlanRequest 模型（推荐）
            ingredients: 可用的食材列表（兼容旧代码）
            preferences: 饮食偏好（可选）
            dietary_restrictions: 饮食限制（可选）

        Returns:
            MealPlanResponse 模型
        """
        # 处理输入
        if request is not None:
            ingredients_list = request.ingredients
            prefs = request.preferences
            restrictions = request.dietary_restrictions
        else:
            if not ingredients:
                raise ValueError("必须提供食材列表")
            # 使用 Pydantic 验证
            request = MealPlanRequest(
                ingredients=ingredients,
                preferences=preferences,
                dietary_restrictions=dietary_restrictions,
            )
            ingredients_list = request.ingredients
            prefs = request.preferences
            restrictions = request.dietary_restrictions

        client = self._get_client()

        # 构建提示词
        ingredients_text = "、".join(ingredients_list)

        system_prompt = """你是一位专业的营养师和烹饪顾问。
你的任务是根据用户提供的食材，设计一份营养均衡、美味健康的一日三餐食谱。

要求：
1. 充分利用用户提供的食材
2. 考虑营养均衡（蛋白质、碳水、脂肪、维生素等）
3. 菜品要实用、易操作
4. 给出每餐的大致热量估算
5. 如有必要，可以建议添加一些常见调料或配菜

输出格式：
🍳 早餐
- 菜品1：[食材] [简单做法]
- 菜品2：...
💡 营养说明：...
📊 估算热量：约 XXX kcal

🍜 午餐
...

🍲 晚餐
..."""

        user_prompt = f"""请根据以下食材设计一日三餐食谱：

可用食材：{ingredients_text}"""

        if prefs:
            user_prompt += f"\n\n饮食偏好：{prefs}"

        if restrictions:
            user_prompt += f"\n\n饮食限制：{restrictions}"

        # 调用 LLM
        try:
            response = client.chat.completions.create(
                model=self.settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            plan_text = response.choices[0].message.content

            return MealPlanResponse(
                ingredients=ingredients_list, plan=plan_text, model_used=self.settings.LLM_MODEL
            )

        except Exception as e:
            raise RuntimeError(f"LLM API 调用失败: {e}") from e


def interactive_meal_planning() -> None:
    """交互式餐食规划"""
    print("\n" + "=" * 60)
    print("🍽️  智能餐食规划助手")
    print("=" * 60)

    # 获取食材
    print("\n请输入你现有的食材（用空格或逗号分隔）:")
    ingredients_input = input("> ").strip()

    if not ingredients_input:
        print("❌ 未输入食材")
        return

    # 解析食材
    ingredients = [
        item.strip()
        for item in ingredients_input.replace("，", ",").replace(" ", ",").split(",")
        if item.strip()
    ]

    print(f"\n识别到的食材：{', '.join(ingredients)}")

    # 获取偏好（可选）
    print("\n是否有特殊饮食偏好？（直接回车跳过）")
    preferences = input("> ").strip()

    # 获取限制（可选）
    print("\n是否有饮食限制？（如：素食、低碳水等，直接回车跳过）")
    restrictions = input("> ").strip()

    # 生成食谱
    print("\n🔄 正在生成食谱，请稍候...")

    try:
        planner = MealPlanner()
        response = planner.generate_meal_plan(
            ingredients=ingredients, preferences=preferences, dietary_restrictions=restrictions
        )

        print("\n" + "=" * 60)
        print(response.plan)
        print("=" * 60)

    except ValueError as e:
        print(f"\n❌ 配置错误: {e}")
        print("\n💡 使用方法:")
        print("   1. 设置环境变量 LOSS_LLM_API_KEY 或在 config.yaml 中配置")
        print("   2. （可选）设置 LOSS_LLM_BASE_URL（默认：https://api.openai.com/v1）")
        print("   3. （可选）设置 LOSS_LLM_MODEL（默认：gpt-3.5-turbo）")
    except RuntimeError as e:
        print(f"\n❌ {e}")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
