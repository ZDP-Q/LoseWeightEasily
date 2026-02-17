from typing import Optional

from ..models import User
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate, UserUpdate


class UserService:
    ACTIVITY_MULTIPLIERS = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }

    def __init__(self, repository: UserRepository):
        self.repo = repository

    def calculate_bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        if gender.lower() == "male":
            return 10 * weight + 6.25 * height - 5 * age + 5
        else:
            return 10 * weight + 6.25 * height - 5 * age - 161

    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        multiplier = self.ACTIVITY_MULTIPLIERS.get(activity_level.lower(), 1.2)
        return bmr * multiplier

    def create_user(self, user_in: UserCreate) -> User:
        db_user = User.model_validate(user_in)
        
        # 自动计算 BMR 和 TDEE
        db_user.bmr = self.calculate_bmr(
            db_user.initial_weight_kg, 
            db_user.height_cm, 
            db_user.age, 
            db_user.gender
        )
        db_user.tdee = self.calculate_tdee(db_user.bmr, db_user.activity_level or "sedentary")
        
        # 如果没有设置每日目标，默认设置为 TDEE - 500 (减重模式)
        if db_user.daily_calorie_goal is None:
            db_user.daily_calorie_goal = max(1200, db_user.tdee - 500)
            
        return self.repo.create_user(db_user)

    def get_user(self) -> Optional[User]:
        return self.repo.get_first_user()

    def update_user(self, user_update: UserUpdate) -> Optional[User]:
        db_user = self.repo.get_first_user()
        if not db_user:
            return None

        user_data = user_update.model_dump(exclude_unset=True)
        
        # 更新后重新计算
        new_weight = user_data.get("initial_weight_kg", db_user.initial_weight_kg)
        new_height = user_data.get("height_cm", db_user.height_cm)
        new_age = user_data.get("age", db_user.age)
        new_gender = user_data.get("gender", db_user.gender)
        new_activity = user_data.get("activity_level", db_user.activity_level)
        
        bmr = self.calculate_bmr(new_weight, new_height, new_age, new_gender)
        tdee = self.calculate_tdee(bmr, new_activity)
        
        user_data["bmr"] = bmr
        user_data["tdee"] = tdee
        
        if "daily_calorie_goal" not in user_data:
            user_data["daily_calorie_goal"] = max(1200, tdee - 500)

        return self.repo.update_user(db_user, user_data)
