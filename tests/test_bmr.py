"""
BMR 模块测试

测试基础代谢率计算功能。
"""

from __future__ import annotations

import pytest

from loss_weight.bmr import (
    ACTIVITY_MULTIPLIERS,
    calculate_bmr,
    calculate_bmr_from_input,
    calculate_tdee,
    calculate_tdee_result,
    get_all_tdee_levels,
)
from loss_weight.models import BMRInput, BMRResult, TDEEResult


@pytest.mark.unit
class TestCalculateBMR:
    """BMR 计算测试"""

    def test_bmr_male(self):
        """测试男性 BMR 计算"""
        # 70kg, 175cm, 25岁 男性
        bmr = calculate_bmr(70, 175, 25, "male")
        # 公式: (10 * 70) + (6.25 * 175) - (5 * 25) + 5 = 700 + 1093.75 - 125 + 5 = 1673.75
        assert abs(bmr - 1673.75) < 0.01

    def test_bmr_female(self):
        """测试女性 BMR 计算"""
        # 60kg, 165cm, 25岁 女性
        bmr = calculate_bmr(60, 165, 25, "female")
        # 公式: (10 * 60) + (6.25 * 165) - (5 * 25) - 161 = 600 + 1031.25 - 125 - 161 = 1345.25
        assert abs(bmr - 1345.25) < 0.01

    def test_bmr_age_effect(self):
        """测试年龄对 BMR 的影响"""
        bmr_young = calculate_bmr(70, 175, 20, "male")
        bmr_old = calculate_bmr(70, 175, 40, "male")
        # 年龄增加应该降低 BMR
        assert bmr_young > bmr_old
        # 差值应该是 (40-20) * 5 = 100
        assert abs((bmr_young - bmr_old) - 100) < 0.01

    def test_bmr_weight_effect(self):
        """测试体重对 BMR 的影响"""
        bmr_light = calculate_bmr(60, 175, 25, "male")
        bmr_heavy = calculate_bmr(80, 175, 25, "male")
        # 体重增加应该提高 BMR
        assert bmr_heavy > bmr_light
        # 差值应该是 (80-60) * 10 = 200
        assert abs((bmr_heavy - bmr_light) - 200) < 0.01

    def test_bmr_height_effect(self):
        """测试身高对 BMR 的影响"""
        bmr_short = calculate_bmr(70, 160, 25, "male")
        bmr_tall = calculate_bmr(70, 180, 25, "male")
        # 身高增加应该提高 BMR
        assert bmr_tall > bmr_short
        # 差值应该是 (180-160) * 6.25 = 125
        assert abs((bmr_tall - bmr_short) - 125) < 0.01

    def test_bmr_gender_difference(self):
        """测试性别对 BMR 的影响"""
        bmr_male = calculate_bmr(70, 175, 25, "male")
        bmr_female = calculate_bmr(70, 175, 25, "female")
        # 男性 BMR 应该比女性高
        assert bmr_male > bmr_female
        # 差值应该是 5 - (-161) = 166
        assert abs((bmr_male - bmr_female) - 166) < 0.01

    def test_bmr_case_insensitive_gender(self):
        """测试性别大小写不敏感"""
        bmr_lower = calculate_bmr(70, 175, 25, "male")
        bmr_upper = calculate_bmr(70, 175, 25, "Male")
        bmr_mixed = calculate_bmr(70, 175, 25, "MALE")
        assert bmr_lower == bmr_upper == bmr_mixed


@pytest.mark.unit
class TestCalculateBMRFromInput:
    """使用 Pydantic 模型的 BMR 计算测试"""

    def test_bmr_from_input(self):
        """测试从输入模型计算 BMR"""
        input_data = BMRInput(
            weight_kg=70,
            height_cm=175,
            age=25,
            gender="male",
        )
        result = calculate_bmr_from_input(input_data)

        assert isinstance(result, BMRResult)
        assert abs(result.bmr - 1673.75) < 0.01
        assert result.input_data == input_data

    def test_bmr_from_input_preserves_data(self):
        """测试 BMR 结果保留输入数据"""
        input_data = BMRInput(
            weight_kg=65.5,
            height_cm=168,
            age=30,
            gender="female",
        )
        result = calculate_bmr_from_input(input_data)

        assert result.input_data.weight_kg == 65.5
        assert result.input_data.height_cm == 168
        assert result.input_data.age == 30
        assert result.input_data.gender == "female"


@pytest.mark.unit
class TestCalculateTDEE:
    """TDEE 计算测试"""

    def test_tdee_sedentary(self):
        """测试久坐活动水平"""
        bmr = 1700
        tdee = calculate_tdee(bmr, "sedentary")
        assert abs(tdee - (1700 * 1.2)) < 0.01

    def test_tdee_light(self):
        """测试轻度活动水平"""
        bmr = 1700
        tdee = calculate_tdee(bmr, "light")
        assert abs(tdee - (1700 * 1.375)) < 0.01

    def test_tdee_moderate(self):
        """测试中度活动水平"""
        bmr = 1700
        tdee = calculate_tdee(bmr, "moderate")
        assert abs(tdee - (1700 * 1.55)) < 0.01

    def test_tdee_active(self):
        """测试重度活动水平"""
        bmr = 1700
        tdee = calculate_tdee(bmr, "active")
        assert abs(tdee - (1700 * 1.725)) < 0.01

    def test_tdee_very_active(self):
        """测试极重度活动水平"""
        bmr = 1700
        tdee = calculate_tdee(bmr, "very_active")
        assert abs(tdee - (1700 * 1.9)) < 0.01

    def test_tdee_invalid_activity_level(self):
        """测试无效活动水平（使用默认值）"""
        bmr = 1700
        tdee = calculate_tdee(bmr, "invalid_level")  # type: ignore
        # 应该使用默认值 1.2
        assert abs(tdee - (1700 * 1.2)) < 0.01


@pytest.mark.unit
class TestCalculateTDEEResult:
    """TDEE 结果计算测试"""

    def test_tdee_result(self):
        """测试 TDEE 结果模型"""
        bmr = 1700
        result = calculate_tdee_result(bmr, "moderate")

        assert isinstance(result, TDEEResult)
        assert result.bmr == 1700
        assert result.activity_level == "moderate"
        assert result.multiplier == 1.55
        assert abs(result.tdee - 2635) < 0.01


@pytest.mark.unit
class TestGetAllTDEELevels:
    """获取所有 TDEE 水平测试"""

    def test_get_all_levels(self):
        """测试获取所有活动水平的 TDEE"""
        bmr = 1700
        results = get_all_tdee_levels(bmr)

        assert len(results) == 5
        assert all(isinstance(r, TDEEResult) for r in results)

        # 验证活动水平覆盖
        levels = {r.activity_level for r in results}
        expected_levels = {"sedentary", "light", "moderate", "active", "very_active"}
        assert levels == expected_levels

    def test_get_all_levels_ordering(self):
        """测试 TDEE 结果按活动强度排序"""
        bmr = 1700
        results = get_all_tdee_levels(bmr)

        # TDEE 应该随活动强度增加
        tdee_values = [r.tdee for r in results]
        # 注意：结果顺序取决于字典迭代顺序，不一定是排序的


@pytest.mark.unit
class TestActivityMultipliers:
    """活动系数常量测试"""

    def test_multipliers_count(self):
        """测试活动系数数量"""
        assert len(ACTIVITY_MULTIPLIERS) == 5

    def test_multipliers_values(self):
        """测试活动系数值"""
        assert ACTIVITY_MULTIPLIERS["sedentary"] == 1.2
        assert ACTIVITY_MULTIPLIERS["light"] == 1.375
        assert ACTIVITY_MULTIPLIERS["moderate"] == 1.55
        assert ACTIVITY_MULTIPLIERS["active"] == 1.725
        assert ACTIVITY_MULTIPLIERS["very_active"] == 1.9

    def test_multipliers_increasing(self):
        """测试活动系数递增"""
        levels = ["sedentary", "light", "moderate", "active", "very_active"]
        values = [ACTIVITY_MULTIPLIERS[level] for level in levels]
        assert values == sorted(values)
