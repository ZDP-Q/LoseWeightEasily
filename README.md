# LossWeightEasily 🍎

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个基于 FAISS 向量语义搜索的智能食物营养信息查询工具，支持中英文跨语言查询。

## ✨ 特性

- 🔍 **智能语义搜索**：基于 FAISS 向量搜索，自动理解语义相似性
- 🌐 **中英文支持**：无需维护翻译词典，自动跨语言匹配
- 📊 **详细营养信息**：显示每100克热量和常用份量的热量
- ⚡ **高性能**：向量索引一次构建，后续查询毫秒级响应
- 🎯 **容错能力**：支持近义词、描述性查询、拼写容错

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/ZDP-Q/LossWeightEasily.git
cd LossWeightEasily

# 使用 uv 安装依赖
uv sync
```

### 使用

#### 交互式查询（推荐）

```bash
uv run python -m loss_weight
```

或者直接运行：

```bash
uv run loss-weight
```

然后输入食物名称即可查询：
- 输入：`番茄` 或 `tomato`
- 输入：`牛肉` 或 `beef`
- 输入：`q` 退出

#### 命令行搜索

```bash
# 搜索特定食物
uv run loss-weight search "番茄"

# 限制返回数量
uv run loss-weight search "beef" -n 5
```

#### 编程方式使用

```python
from loss_weight import query_food_calories, FoodSearchEngine

# 简单查询
query_food_calories("番茄")

# 使用搜索引擎获取详细信息
engine = FoodSearchEngine()
engine.ensure_index()

results = engine.search_with_details("tomato", limit=5)
for food in results:
    print(f"{food['name']}: {food['calories_per_100g']} kcal/100g")
```

## 📁 项目结构

```
LossWeightEasily/
├── src/
│   └── loss_weight/          # 主要源代码
│       ├── __init__.py       # 包初始化
│       ├── cli.py            # 命令行接口
│       ├── config.py         # 配置管理
│       ├── database.py       # 数据库操作
│       ├── query.py          # 查询接口
│       └── search.py         # 搜索引擎
├── tests/                    # 测试代码
├── docs/                     # 文档
├── data/                     # 数据文件
├── pyproject.toml            # 项目配置
└── README.md                 # 项目说明
```

## 🛠️ 命令行工具

```bash
# 初始化数据库和索引
uv run loss-weight init

# 交互式查询
uv run loss-weight interactive

# 搜索食物
uv run loss-weight search "关键词"

# 查看数据库统计
uv run loss-weight stats

# 重建搜索索引
uv run loss-weight rebuild-index
```

## 🔧 技术栈

- **Python 3.10+**
- **FAISS** - Facebook AI 的高效相似性搜索库
- **Sentence-Transformers** - 多语言语义嵌入模型
- **SQLite** - 轻量级本地数据库
- **uv** - 现代 Python 包管理器

## 📊 数据来源

食物营养数据来自 [USDA FoodData Central](https://fdc.nal.usda.gov/) Foundation Foods 数据集。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
