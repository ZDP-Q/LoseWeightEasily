"""
UI 页面模块
"""

from .bmr import BMRPage
from .dashboard import DashboardPage
from .food_search import FoodSearchPage
from .meal_plan import MealPlanPage
from .settings import SettingsPage
from .weight import WeightPage

__all__ = [
    "DashboardPage",
    "WeightPage",
    "FoodSearchPage",
    "BMRPage",
    "MealPlanPage",
    "SettingsPage",
]
