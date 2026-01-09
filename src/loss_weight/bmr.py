"""
基础代谢率 (BMR) 计算模块

提供基于 Mifflin-St Jeor 公式的 BMR 计算功能。
"""

from typing import Literal

Gender = Literal["male", "female"]

def calculate_bmr(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: Gender
) -> float:
    """
    计算基础代谢率 (Mifflin-St Jeor 公式)

    Args:
        weight_kg: 体重 (kg)
        height_cm: 身高 (cm)
        age: 年龄 (岁)
        gender: 性别 ('male' 或 'female')

    Returns:
        BMR 数值 (kcal/day)

    Formula:
        Men: (10 × weight) + (6.25 × height) - (5 × age) + 5
        Women: (10 × weight) + (6.25 × height) - (5 × age) - 161
    """
    base_bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)

    if gender.lower() == "male":
        return base_bmr + 5
    else:
        return base_bmr - 161

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    计算每日总能量消耗 (TDEE)

    Args:
        bmr: 基础代谢率
        activity_level: 活动水平描述

    Returns:
        TDEE 数值 (kcal/day)
    """
    multipliers = {
        "sedentary": 1.2,      # 久坐 (办公室工作，很少运动)
        "light": 1.375,        # 轻度活动 (每周运动 1-3 天)
        "moderate": 1.55,      # 中度活动 (每周运动 3-5 天)
        "active": 1.725,       # 重度活动 (每周运动 6-7 天)
        "very_active": 1.9     # 极重度活动 (体力工作 或 双倍训练)
    }

    return bmr * multipliers.get(activity_level, 1.2)
