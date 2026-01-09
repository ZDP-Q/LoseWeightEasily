"""
餐食规划模块

基于食材和营养信息，使用 LLM 生成一日三餐食谱。
"""


from openai import OpenAI

from .config import config
from .database import DatabaseManager


class MealPlanner:
    """餐食规划器"""

    def __init__(self, db_path: str = None):
        """
        初始化餐食规划器

        Args:
            db_path: 数据库路径
        """
        self.db_manager = DatabaseManager(db_path)
        self.client: OpenAI | None = None

    def _get_client(self) -> OpenAI:
        """获取 OpenAI 客户端（懒加载）"""
        if self.client is None:
            if not config.LLM_API_KEY:
                raise ValueError(
                    "未配置 LLM API Key。请设置环境变量 LOSS_LLM_API_KEY"
                )
            self.client = OpenAI(
                api_key=config.LLM_API_KEY,
                base_url=config.LLM_BASE_URL
            )
        return self.client

    def get_ingredient_nutrition(self, ingredient: str) -> dict | None:
        """
        获取食材的营养信息

        Args:
            ingredient: 食材名称

        Returns:
            营养信息字典，包含热量等数据
        """
        # 通过数据库搜索获取营养信息
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        # 简单模糊搜索
        cursor.execute("""
            SELECT f.fdc_id, f.description, f.food_category
            FROM foods f
            WHERE f.description LIKE ?
            LIMIT 1
        """, (f"%{ingredient}%",))

        result = cursor.fetchone()
        conn.close()

        if result:
            fdc_id = result[0]
            return self.db_manager.get_food_complete_info(fdc_id)
        return None

    def generate_meal_plan(
        self,
        ingredients: list[str],
        preferences: str = "",
        dietary_restrictions: str = ""
    ) -> str:
        """
        生成一日三餐食谱

        Args:
            ingredients: 可用的食材列表
            preferences: 饮食偏好（可选）
            dietary_restrictions: 饮食限制（可选）

        Returns:
            生成的食谱文本
        """
        client = self._get_client()

        # 构建提示词
        ingredients_text = "、".join(ingredients)

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

        if preferences:
            user_prompt += f"\n\n饮食偏好：{preferences}"

        if dietary_restrictions:
            user_prompt += f"\n\n饮食限制：{dietary_restrictions}"

        # 调用 LLM
        try:
            response = client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

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
        meal_plan = planner.generate_meal_plan(
            ingredients=ingredients,
            preferences=preferences,
            dietary_restrictions=restrictions
        )

        print("\n" + "=" * 60)
        print(meal_plan)
        print("=" * 60)

    except ValueError as e:
        print(f"\n❌ 配置错误: {e}")
        print("\n💡 使用方法:")
        print("   1. 设置环境变量 LOSS_LLM_API_KEY")
        print("   2. （可选）设置 LOSS_LLM_BASE_URL（默认：https://api.openai.com/v1）")
        print("   3. （可选）设置 LOSS_LLM_MODEL（默认：gpt-3.5-turbo）")
    except RuntimeError as e:
        print(f"\n❌ {e}")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
