"""
LossWeightEasily - 食物卡路里查询系统

一个基于 FAISS 向量语义搜索的智能食物营养信息查询工具。
支持中英文跨语言查询，自动理解语义相似性。
"""

from .database import DatabaseManager
from .search import FoodSearchEngine
from .query import query_food_calories, interactive_query

__version__ = "0.2.0"
__author__ = "ZDP-Q"

__all__ = [
    "DatabaseManager",
    "FoodSearchEngine", 
    "query_food_calories",
    "interactive_query",
]
