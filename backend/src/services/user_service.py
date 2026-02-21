from typing import Optional

from ..models import User
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate, UserProfileUpdate
from ..core.security import get_password_hash


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

    def calculate_bmr(
        self, weight: float, height: float, age: int, gender: str
    ) -> float:
        if gender.lower() == "male":
            return 10 * weight + 6.25 * height - 5 * age + 5
        else:
            return 10 * weight + 6.25 * height - 5 * age - 161

    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        multiplier = self.ACTIVITY_MULTIPLIERS.get(activity_level.lower(), 1.2)
        return bmr * multiplier

    def register_user(self, user_in: UserCreate) -> User:
        # 检查用户是否已存在
        existing_user = self.repo.get_user_by_username(user_in.username)
        if existing_user:
            raise ValueError("Username already exists")

        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            username=user_in.username,
            hashed_password=hashed_password,
            email=user_in.email,
        )
        return self.repo.create_user(db_user)

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.repo.get_user_by_username(username)

    def update_profile(self, user: User, profile: UserProfileUpdate) -> User:
        """更新用户个人身体资料并自动计算代谢指标。"""
        data = profile.model_dump()

        # 重新计算 BMR 和 TDEE
        bmr = self.calculate_bmr(
            data["initial_weight_kg"], data["height_cm"], data["age"], data["gender"]
        )
        tdee = self.calculate_tdee(bmr, data["activity_level"])

        data["bmr"] = bmr
        data["tdee"] = tdee

        # 默认设置为减重目标 (TDEE - 500)
        data["daily_calorie_goal"] = max(1200, tdee - 500)

        return self.repo.update_user(user, data)
