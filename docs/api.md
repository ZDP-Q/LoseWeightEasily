# API 参考文档

## 模块概览

```
loss_weight/
├── config.py      # 配置管理
├── database.py    # 数据库操作
├── search.py      # 搜索引擎
├── query.py       # 查询接口
└── cli.py         # 命令行接口
```

## Config 模块

### `Config` 类

配置管理类，支持环境变量覆盖。

```python
from loss_weight.config import config

# 属性
config.DB_PATH              # 数据库路径
config.INDEX_FILE           # FAISS 索引文件
config.METADATA_FILE        # 元数据文件
config.EMBEDDING_MODEL      # 嵌入模型名称
config.DEFAULT_SEARCH_LIMIT # 默认搜索限制
config.SIMILARITY_THRESHOLD # 相似度阈值

# 方法
config.get_json_data_path() # 获取 JSON 数据文件路径
config.database_exists()    # 检查数据库是否存在
config.index_exists()       # 检查索引是否存在
```

## Database 模块

### `DatabaseManager` 类

数据库管理器，负责数据存储和查询。

```python
from loss_weight.database import DatabaseManager

db = DatabaseManager(db_path="food_data.db")

# 创建表结构
db.create_tables()

# 从 JSON 导入数据
stats = db.import_from_json("data/food.json")

# 获取统计信息
stats = db.get_statistics()
# 返回: {"foods": 365, "nutrients": 150, ...}

# 获取所有食物
foods = db.get_all_foods()
# 返回: [(fdc_id, description, category), ...]

# 获取食物信息
info = db.get_food_info(fdc_id=123456)
# 返回: (description, category)

# 获取卡路里
calories = db.get_food_calories(fdc_id=123456)
# 返回: (amount, unit_name)

# 获取份量信息
portions = db.get_food_portions(fdc_id=123456, limit=3)
# 返回: [(amount, unit_name, gram_weight), ...]

# 获取完整信息
info = db.get_food_complete_info(fdc_id=123456)
# 返回: {
#     "name": "...",
#     "category": "...",
#     "calories_per_100g": 100.0,
#     "unit": "kcal",
#     "portions": [...]
# }
```

## Search 模块

### `FoodSearchEngine` 类

基于 FAISS 的语义搜索引擎。

```python
from loss_weight.search import FoodSearchEngine

engine = FoodSearchEngine(db_path="food_data.db")

# 确保索引已加载
engine.ensure_index()

# 构建/重建索引
engine.build_index(force_rebuild=False)

# 搜索食物
results = engine.search(
    query="番茄",
    limit=10,
    threshold=0.3
)
# 返回: [(fdc_id, description, category, similarity), ...]

# 搜索并获取详情
details = engine.search_with_details(
    query="apple",
    limit=5
)
# 返回: [{
#     "name": "...",
#     "category": "...",
#     "calories_per_100g": 52.0,
#     "unit": "kcal",
#     "portions": [...],
#     "similarity": 0.85
# }, ...]
```

## Query 模块

### 函数

```python
from loss_weight.query import (
    query_food_calories,
    interactive_query,
    initialize_system
)

# 查询食物卡路里（打印结果）
query_food_calories(
    search_term="番茄",
    db_path="food_data.db",
    limit=10
)

# 启动交互式查询
interactive_query(db_path="food_data.db")

# 初始化系统
initialize_system(
    db_path="food_data.db",
    force_rebuild=False
)
```

## CLI 模块

命令行接口，支持以下命令：

```bash
# 交互式查询
loss-weight [interactive]

# 搜索食物
loss-weight search <query> [-n LIMIT]

# 初始化系统
loss-weight init [--force]

# 查看统计
loss-weight stats

# 重建索引
loss-weight rebuild-index
```

## 类型定义

### FoodInfo

```python
FoodInfo = {
    "name": str,              # 食物名称
    "category": str | None,   # 分类
    "calories_per_100g": float | None,  # 每100g热量
    "unit": str | None,       # 单位
    "portions": List[Tuple[float, str, float]]  # 份量信息
}
```

### SearchResult

```python
SearchResult = Tuple[
    int,    # fdc_id
    str,    # description
    str,    # category
    float   # similarity
]
```
