"""
基础代谢率 (BMR) 计算模块

提供基于 Mifflin-St Jeor 公式的 BMR 计算功能。
使用 Pydantic 模型确保数据验证。
"""

from __future__ import annotations

from .models import (
    ActivityLevel,
    BMRInput,
    BMRResult,
    Gender,
    TDEEResult,
)

# 活动系数
ACTIVITY_MULTIPLIERS: dict[ActivityLevel, float] = {
    "sedentary": 1.2,  # 久坐 (办公室工作，很少运动)
    "light": 1.375,  # 轻度活动 (每周运动 1-3 天)
    "moderate": 1.55,  # 中度活动 (每周运动 3-5 天)
    "active": 1.725,  # 重度活动 (每周运动 6-7 天)
    "very_active": 1.9,  # 极重度活动 (体力工作 或 双倍训练)
}


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: Gender) -> float:
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


def calculate_bmr_from_input(input_data: BMRInput) -> BMRResult:
    """
    使用 Pydantic 模型计算 BMR

    Args:
        input_data: BMRInput 模型

    Returns:
        BMRResult 模型
    """
    bmr = calculate_bmr(
        weight_kg=input_data.weight_kg,
        height_cm=input_data.height_cm,
        age=input_data.age,
        gender=input_data.gender,
    )
    return BMRResult(bmr=bmr, input_data=input_data)


def calculate_tdee(bmr: float, activity_level: ActivityLevel) -> float:
    """
    计算每日总能量消耗 (TDEE)

    Args:
        bmr: 基础代谢率
        activity_level: 活动水平描述

    Returns:
        TDEE 数值 (kcal/day)
    """
    return bmr * ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)


def calculate_tdee_result(bmr: float, activity_level: ActivityLevel) -> TDEEResult:
    """
    计算 TDEE 并返回详细结果

    Args:
        bmr: 基础代谢率
        activity_level: 活动水平

    Returns:
        TDEEResult 模型
    """
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    tdee = bmr * multiplier
    return TDEEResult(bmr=bmr, activity_level=activity_level, tdee=tdee, multiplier=multiplier)


def get_all_tdee_levels(bmr: float) -> list[TDEEResult]:
    """
    获取所有活动水平的 TDEE

    Args:
        bmr: 基础代谢率

    Returns:
        所有活动水平的 TDEEResult 列表
    """
    return [calculate_tdee_result(bmr, level) for level in ACTIVITY_MULTIPLIERS.keys()]
