from typing import Dict, List, Any, Optional

from sqlmodel import Session, select

from ..models import Food


class FoodRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_food_by_id(self, fdc_id: int) -> Optional[Food]:
        statement = select(Food).where(Food.fdc_id == fdc_id)
        return self.session.exec(statement).first()

    def get_foods_by_ids(self, fdc_ids: List[int]) -> Dict[int, Food]:
        """批量查询食物，返回 {fdc_id: Food} 的字典，解决 N+1 查询问题。"""
        if not fdc_ids:
            return {}
        statement = select(Food).where(Food.fdc_id.in_(fdc_ids))  # type: ignore[attr-defined]
        foods = self.session.exec(statement).all()
        return {food.fdc_id: food for food in foods}

    @staticmethod
    def extract_calories(food: Food) -> Optional[float]:
        """从食物的营养素列表中提取热量（kcal/100g）。"""
        for fn in food.nutrients:
            # 208 是 Energy (kcal) 的标准营养素编号
            if fn.nutrient and fn.nutrient.nutrient_number == "208":
                return fn.amount
        return None

    def get_foods_simple_details(self, fdc_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """批量获取食物的简要信息（描述、分类、热量）。"""
        foods_map = self.get_foods_by_ids(fdc_ids)
        result: Dict[int, Dict[str, Any]] = {}
        for fdc_id, food in foods_map.items():
            result[fdc_id] = {
                "fdc_id": food.fdc_id,
                "description": food.description,
                "category": food.food_category,
                "calories_per_100g": self.extract_calories(food),
            }
        return result
