from typing import Dict


class BMRService:
    @staticmethod
    def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
        if gender.lower() == "male":
            return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        factors = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }
        return bmr * factors.get(activity_level, 1.2)

    @classmethod
    def get_all_tdee_levels(cls, bmr: float) -> Dict[str, float]:
        levels = ["sedentary", "light", "moderate", "active", "very_active"]
        return {level: cls.calculate_tdee(bmr, level) for level in levels}
