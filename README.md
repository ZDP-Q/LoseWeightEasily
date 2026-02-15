# LoseWeightEasily 🍎

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个帮助你轻松减重的智能健康管理工具，提供食物营养查询、体重记录、基础代谢计算和智能食谱规划等功能。

## ✨ 特性

- 🔍 **智能食物搜索**：基于 FAISS 语义搜索，支持中英文跨语言查询
- ⚖️ **体重记录管理**：每日体重打卡，自动统计变化趋势
- 🔥 **代谢率计算**：计算基础代谢率 (BMR) 和每日总消耗 (TDEE)
- 🍽️ **智能食谱规划**：根据现有食材生成营养均衡的一日三餐
- 📊 **详细营养信息**：显示每100克热量和常用份量的热量
- ⚡ **高性能响应**：向量索引一次构建，后续查询毫秒级响应

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/ZDP-Q/LossWeightEasily.git
cd LossWeightEasily

# 使用 uv 安装依赖
uv sync
```

### 配置 LLM API（可选）

食谱规划功能需要配置 LLM API。支持两种配置方式：

**方法 1：使用 config.yaml（推荐）**

1. 复制示例配置文件：
```bash
cp config.yaml.example config.yaml
```

2. 编辑 `config.yaml`，填写你的 API Key：
```yaml
llm:
  api_key: "your-api-key-here"
  base_url: "https://api.openai.com/v1"  # 可选
  model: "gpt-3.5-turbo"  # 可选
```

**方法 2：使用环境变量**

```bash
# PowerShell
$env:LOSS_LLM_API_KEY="your-api-key"
$env:LOSS_LLM_BASE_URL="https://api.openai.com/v1"
$env:LOSS_LLM_MODEL="gpt-3.5-turbo"
```

配置优先级：环境变量 > config.yaml > 默认值

支持的 LLM 服务：
- OpenAI (gpt-3.5-turbo, gpt-4)
- DeepSeek (deepseek-chat)
- 智谱 AI (glm-4)
- 通义千问 (qwen-max)

### 使用

#### 图形界面（推荐）

```bash
uv run loss-weight-ui
```

提供完整的图形化界面：
- 📊 仪表盘：查看 BMR、TDEE 和体重统计
- ⚖️ 体重记录：输入体重，查看趋势曲线
- 🔍 食物搜索：智能语义搜索食物营养信息
- 🔥 BMR 计算：计算基础代谢和每日总消耗
- 🍽️ 食谱规划：AI 生成营养均衡的一日三餐
- ⚙️ 设置：查看和配置应用参数

#### 命令行界面

**交互式查询**

```bash
uv run loss-weight
# 或
uv run python -m loss_weight
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
│       ├── models.py         # Pydantic 数据模型
│       ├── container.py      # 依赖注入容器
│       ├── config.py         # Pydantic Settings 配置
│       ├── cli.py            # 命令行接口
│       ├── database.py       # 数据库操作
│       ├── search.py         # FAISS 搜索引擎
│       ├── query.py          # 查询接口
│       ├── bmr.py            # BMR/TDEE 计算
│       ├── weight_tracker.py # 体重记录
│       ├── meal_planner.py   # AI 食谱规划
│       └── ui/               # PySide6 GUI
│           ├── __init__.py   # UI 入口
│           ├── main_window.py # 主窗口
│           ├── styles.py     # 样式常量
│           └── pages/        # UI 页面
├── tests/                    # 测试代码
├── docs/                     # 文档
├── data/                     # 数据文件
├── pyproject.toml            # 项目配置
└── README.md                 # 项目说明
```

## 🏗️ 架构特性

- **Pydantic v2 数据模型**: 所有数据结构使用 Pydantic 模型确保类型安全
- **依赖注入容器**: 集中管理服务实例，支持懒加载
- **Lazy Import**: 延迟导入重型依赖（FAISS、sentence-transformers）加快启动
- **上下文管理器**: 数据库连接自动管理，避免资源泄漏

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
- **Pydantic v2** - 数据验证和类型安全
- **pydantic-settings** - 配置管理
- **FAISS** - Facebook AI 的高效相似性搜索库
- **Sentence-Transformers** - 多语言语义嵌入模型
- **SQLite** - 轻量级本地数据库
- **PySide6** - 跨平台 GUI 框架
- **OpenAI API** - LLM 食谱规划
- **uv** - 现代 Python 包管理器

## 📊 数据来源

食物营养数据来自 [USDA FoodData Central](https://fdc.nal.usda.gov/) Foundation Foods 数据集。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
