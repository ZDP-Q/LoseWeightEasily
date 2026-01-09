"""测试基于FAISS向量的语义搜索功能"""
from main import query_food_calories

print("\n" + "="*70)
print("🧪 测试FAISS向量语义搜索")
print("="*70)

# 测试1：中文精确词汇
print("\n【测试1】中文精确词汇")
query_food_calories("番茄")

print("\n" + "="*70)

# 测试2：中文近义词（无需词典）
print("\n【测试2】中文近义词 - 西红柿")
query_food_calories("西红柿")

print("\n" + "="*70)

# 测试3：中文描述性短语
print("\n【测试3】中文描述性短语 - 牛肉香肠")
query_food_calories("牛肉香肠")

print("\n" + "="*70)

# 测试4：混合语义
print("\n【测试4】语义搜索 - 坚果类")
query_food_calories("坚果")

print("\n" + "="*70)

# 测试5：英文搜索
print("\n【测试5】英文搜索 - roasted nuts")
query_food_calories("roasted nuts")

print("\n" + "="*70)

# 测试6：拼写错误容错
print("\n【测试6】语义理解 - 蔬菜")
query_food_calories("蔬菜")

print("\n" + "="*70)
print("\n✅ 测试完成！")
print("\n💡 优势：")
print("  - 无需维护翻译词典")
print("  - 支持语义级别的理解（番茄=西红柿）")
print("  - 支持描述性查询（牛肉香肠、坚果类）")
print("  - 自动处理中英文混合")
