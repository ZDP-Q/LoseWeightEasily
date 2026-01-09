# 🍎 食物卡路里查询系统

## 功能特点

✨ **支持中英文查询**：可以使用中文或英文搜索食物
🔍 **智能模糊搜索**：自动匹配相似的食物名称
📊 **详细营养信息**：显示每100克的热量和常用份量的热量
🌐 **中英文翻译**：内置常见食物的中英文对照

## 使用方法

### 1. 交互式查询（推荐）

直接运行程序，进入交互式查询界面：

```bash
python main.py
```

然后输入食物名称即可查询，例如：
- 输入：`番茄` 或 `tomato`
- 输入：`热狗` 或 `frankfurter`
- 输入：`杏仁` 或 `almond`
- 输入：`q` 或 `quit` 退出

### 2. 编程方式查询

```python
from main import query_food_calories

# 查询番茄的卡路里
query_food_calories("番茄")

# 查询牛肉的卡路里
query_food_calories("beef")
```

## 查询示例

### 中文查询示例

```
请输入食物名称: 番茄

🔍 搜索: 番茄
============================================================

找到 9 个匹配结果:

1. Tomatoes, grape, raw
   分类: Vegetables and Vegetable Products
   📊 热量: 27.0 kcal/100g
   📏 常用份量:
      • 5.0 tomatoes (49.7g) = 13.4 kcal
      • 1.0 RACC (85.0g) = 22.9 kcal
```

### 英文查询示例

```
请输入食物名称: beef

🔍 搜索: beef
============================================================

找到 10 个匹配结果:

1. Frankfurter, beef, unheated
   分类: Sausages and Luncheon Meats
   📊 热量: 314.0 kcal/100g
   📏 常用份量:
      • 1.0 piece (48.6g) = 152.6 kcal
      • 1.0 RACC (85.0g) = 266.9 kcal
```

## 支持的中文食物名称

### 蔬菜类
- 番茄/西红柿 → tomato
- 圣女果 → grape tomato
- 豆角/四季豆/青豆 → green bean
- 胡萝卜/红萝卜 → carrot
- 土豆/马铃薯 → potato
- 玉米、黄瓜、生菜、菠菜、西兰花等

### 肉类
- 牛肉 → beef
- 猪肉 → pork
- 鸡肉 → chicken
- 热狗/热狗肠 → frankfurter
- 香肠 → sausage
- 培根、火腿等

### 坚果类
- 杏仁/扁桃仁 → almond
- 核桃 → walnut
- 花生 → peanut
- 腰果、开心果等

### 水果类
- 苹果、香蕉、橙子、葡萄等

### 谷物类
- 米饭、面包、面条、燕麦等

### 乳制品
- 牛奶、酸奶、奶酪、黄油等

## 数据来源

数据来自美国农业部食品数据中心（USDA FoodData Central）Foundation Food 数据集，包含365种食品的详细营养信息。

## 技术实现

- **数据库**：SQLite
- **中英文翻译**：内置词典映射
- **模糊搜索**：基于字符串相似度算法
- **营养数据**：228种营养素，15,391条食品-营养素关联

## 文件说明

- `main.py` - 主程序（包含数据导入和查询功能）
- `test_query.py` - 测试脚本
- `food_data.db` - SQLite数据库文件
- `FoodData_Central_foundation_food_json_2025-12-18.json` - 原始JSON数据

## 扩展词典

如果需要添加更多中英文翻译，可以在 `main.py` 中的 `FOOD_TRANSLATION` 字典里添加：

```python
FOOD_TRANSLATION = {
    "你的中文食物名": "english food name",
    # 添加更多...
}
```

## 注意事项

1. 首次运行会自动导入JSON数据到SQLite数据库
2. 卡路里数值是每100克的热量（kcal）
3. 不同烹饪方式的食物热量可能不同
4. 搜索时会返回最多10个匹配结果
