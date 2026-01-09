"""
Pydantic 数据模型测试

测试所有 Pydantic 模型的验证和序列化功能。
"""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from loss_weight.models import (
    BMRInput,
    BMRResult,
    DatabaseStatistics,
    Food,
    FoodCompleteInfo,
    FoodNutrient,
    FoodPortion,
    FoodSearchResult,
    MealPlanRequest,
    MealPlanResponse,
    Nutrient,
    SearchQuery,
    TDEEResult,
    WeightRecord,
    WeightRecordCreate,
    WeightStatistics,
)


@pytest.mark.unit
class TestNutrientModel:
    """营养素模型测试"""

    def test_create_nutrient(self):
        """测试创建营养素"""
        nutrient = Nutrient(
            nutrient_id=1003,
            nutrient_number="203",
            nutrient_name="Protein",
            unit_name="g",
            rank=600,
        )
        assert nutrient.nutrient_id == 1003
        assert nutrient.nutrient_name == "Protein"

    def test_nutrient_optional_fields(self):
        """测试营养素可选字段"""
        nutrient = Nutrient(nutrient_id=1003)
        assert nutrient.nutrient_number is None
        assert nutrient.nutrient_name is None


@pytest.mark.unit
class TestFoodModels:
    """食品相关模型测试"""

    def test_create_food(self):
        """测试创建食品"""
        food = Food(
            fdc_id=167512,
            description="Apple, raw",
            food_class="Survey",
            food_category="Fruits",
        )
        assert food.fdc_id == 167512
        assert food.description == "Apple, raw"

    def test_food_search_result(self):
        """测试食品搜索结果"""
        result = FoodSearchResult(
            fdc_id=167512,
            description="Apple, raw",
            category="Fruits",
            similarity=0.95,
        )
        assert result.fdc_id == 167512
        assert result.similarity == 0.95

    def test_food_search_result_similarity_validation(self):
        """测试相似度验证"""
        # 有效范围
        result = FoodSearchResult(
            fdc_id=1, description="Test", similarity=0.0
        )
        assert result.similarity == 0.0

        result = FoodSearchResult(
            fdc_id=1, description="Test", similarity=1.0
        )
        assert result.similarity == 1.0

        # 无效范围
        with pytest.raises(ValidationError):
            FoodSearchResult(fdc_id=1, description="Test", similarity=1.5)

        with pytest.raises(ValidationError):
            FoodSearchResult(fdc_id=1, description="Test", similarity=-0.1)

    def test_food_complete_info(self):
        """测试食品完整信息"""
        info = FoodCompleteInfo(
            name="Apple",
            category="Fruits",
            calories_per_100g=52.0,
            unit="kcal",
            portions=[(1.0, "medium", 182.0)],
            similarity=0.9,
        )
        assert info.name == "Apple"
        assert info.calories_per_100g == 52.0
        assert len(info.portions) == 1


@pytest.mark.unit
class TestWeightModels:
    """体重相关模型测试"""

    def test_create_weight_record(self):
        """测试创建体重记录"""
        record = WeightRecord(
            id=1,
            weight_kg=70.5,
            recorded_at=datetime.now(),
            notes="早餐前",
        )
        assert record.weight_kg == 70.5
        assert record.notes == "早餐前"

    def test_weight_record_validation(self):
        """测试体重验证"""
        # 有效体重
        record = WeightRecordCreate(weight_kg=70.5)
        assert record.weight_kg == 70.5

        # 体重过大
        with pytest.raises(ValidationError):
            WeightRecordCreate(weight_kg=501)

        # 体重为负
        with pytest.raises(ValidationError):
            WeightRecordCreate(weight_kg=-10)

        # 体重为零
        with pytest.raises(ValidationError):
            WeightRecordCreate(weight_kg=0)

    def test_weight_record_create_rounding(self):
        """测试体重四舍五入"""
        record = WeightRecordCreate(weight_kg=70.555)
        assert record.weight_kg == 70.56

    def test_weight_statistics(self):
        """测试体重统计"""
        stats = WeightStatistics(
            total_records=10,
            latest_weight=70.0,
            latest_date="2024-01-01",
            weight_change=-2.5,
            average_weight=71.0,
        )
        assert stats.total_records == 10
        assert stats.weight_change == -2.5


@pytest.mark.unit
class TestBMRModels:
    """BMR 相关模型测试"""

    def test_create_bmr_input(self):
        """测试创建 BMR 输入"""
        input_data = BMRInput(
            weight_kg=70,
            height_cm=175,
            age=25,
            gender="male",
        )
        assert input_data.weight_kg == 70
        assert input_data.gender == "male"

    def test_bmr_input_validation(self):
        """测试 BMR 输入验证"""
        # 有效输入
        input_data = BMRInput(
            weight_kg=70, height_cm=175, age=25, gender="female"
        )
        assert input_data.gender == "female"

        # 无效性别
        with pytest.raises(ValidationError):
            BMRInput(weight_kg=70, height_cm=175, age=25, gender="other")

        # 身高过低
        with pytest.raises(ValidationError):
            BMRInput(weight_kg=70, height_cm=40, age=25, gender="male")

        # 年龄为负
        with pytest.raises(ValidationError):
            BMRInput(weight_kg=70, height_cm=175, age=-5, gender="male")

    def test_bmr_result(self):
        """测试 BMR 结果"""
        input_data = BMRInput(
            weight_kg=70, height_cm=175, age=25, gender="male"
        )
        result = BMRResult(bmr=1700.0, input_data=input_data)
        assert result.bmr == 1700.0
        assert result.input_data.weight_kg == 70

    def test_tdee_result(self):
        """测试 TDEE 结果"""
        result = TDEEResult(
            bmr=1700.0,
            activity_level="moderate",
            tdee=2635.0,
            multiplier=1.55,
        )
        assert result.tdee == 2635.0
        assert result.activity_level == "moderate"


@pytest.mark.unit
class TestMealPlanModels:
    """餐食规划相关模型测试"""

    def test_create_meal_plan_request(self):
        """测试创建餐食规划请求"""
        request = MealPlanRequest(
            ingredients=["鸡胸肉", "西兰花", "米饭"],
            preferences="低碳水",
            dietary_restrictions="无坚果",
        )
        assert len(request.ingredients) == 3
        assert request.preferences == "低碳水"

    def test_meal_plan_request_defaults(self):
        """测试餐食规划请求默认值"""
        request = MealPlanRequest(ingredients=["鸡蛋"])
        assert request.preferences == ""
        assert request.dietary_restrictions == ""

    def test_meal_plan_response(self):
        """测试餐食规划响应"""
        response = MealPlanResponse(
            ingredients=["鸡蛋", "西红柿"],
            plan="早餐：煎蛋\n午餐：鸡胸沙拉\n晚餐：蒸鱼",
            model_used="gpt-3.5-turbo",
        )
        assert len(response.ingredients) == 2
        assert "早餐" in response.plan
        assert response.model_used == "gpt-3.5-turbo"


@pytest.mark.unit
class TestSearchQuery:
    """搜索查询模型测试"""

    def test_create_search_query(self):
        """测试创建搜索查询"""
        query = SearchQuery(query="番茄", limit=5, threshold=0.5)
        assert query.query == "番茄"
        assert query.limit == 5
        assert query.threshold == 0.5

    def test_search_query_defaults(self):
        """测试搜索查询默认值"""
        query = SearchQuery(query="apple")
        # 有默认值
        assert query.limit == 10
        assert query.threshold == 0.3

    def test_search_query_validation(self):
        """测试搜索查询验证"""
        # 空查询
        with pytest.raises(ValidationError):
            SearchQuery(query="")

        # limit 过大
        with pytest.raises(ValidationError):
            SearchQuery(query="test", limit=1000)

        # threshold 超出范围
        with pytest.raises(ValidationError):
            SearchQuery(query="test", threshold=1.5)


@pytest.mark.unit
class TestDatabaseStatistics:
    """数据库统计模型测试"""

    def test_create_database_statistics(self):
        """测试创建数据库统计"""
        stats = DatabaseStatistics(
            foods=1000,
            nutrients=50,
            food_nutrients=50000,
            portions=2000,
        )
        assert stats.foods == 1000
        assert stats.nutrients == 50

    def test_database_statistics_defaults(self):
        """测试数据库统计默认值"""
        stats = DatabaseStatistics()
        assert stats.foods == 0
        assert stats.nutrients == 0
