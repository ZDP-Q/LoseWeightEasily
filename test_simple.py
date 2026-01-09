"""简单测试FAISS向量搜索"""
from main import build_food_index, search_food_by_name

print("\n🔨 构建向量索引...")
build_food_index("food_data.db")

print("\n" + "="*60)
print("测试1: 搜索 '番茄'")
results = search_food_by_name("food_data.db", "番茄", limit=5)
for fdc_id, desc, category in results:
    print(f"  - {desc} ({category})")

print("\n" + "="*60)
print("测试2: 搜索 '西红柿' (番茄的同义词)")
results = search_food_by_name("food_data.db", "西红柿", limit=5)
for fdc_id, desc, category in results:
    print(f"  - {desc} ({category})")

print("\n" + "="*60)
print("测试3: 搜索 '热狗'")
results = search_food_by_name("food_data.db", "热狗", limit=5)
for fdc_id, desc, category in results:
    print(f"  - {desc} ({category})")

print("\n✅ 向量搜索测试完成！")
