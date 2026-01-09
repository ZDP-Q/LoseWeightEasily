"""测试食物卡路里查询功能"""
from main import query_food_calories

# 测试中文查询
print("\n测试1: 中文查询 - 番茄")
query_food_calories("番茄")

print("\n" + "="*60)
print("\n测试2: 中文查询 - 热狗")
query_food_calories("热狗")

print("\n" + "="*60)
print("\n测试3: 英文查询 - beef")
query_food_calories("beef")

print("\n" + "="*60)
print("\n测试4: 中文查询 - 杏仁")
query_food_calories("杏仁")
