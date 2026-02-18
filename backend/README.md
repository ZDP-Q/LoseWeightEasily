# LoseWeightEasily 后端 🚀

基于 FastAPI 的高性能健康管理 API 服务。

## 🛠️ 技术栈

- **框架**: [FastAPI](https://fastapi.tiangolo.com/)
- **数据库 ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) (结合了 SQLAlchemy 和 Pydantic)
- **数据库**: PostgreSQL
- **语义搜索**: [Milvus](https://milvus.io/) (向量数据库)
- **嵌入模型**: `qwen3-vl-embedding` (DashScope / Qwen)
- **包管理**: [uv](https://github.com/astral-sh/uv)
- **代码规范**: [Ruff](https://github.com/astral-sh/ruff)

## 🏗️ 项目结构

```text
src/
├── api/            # 接口层：定义 HTTP 路由
├── core/           # 核心层：配置管理 (config.py)、数据库连接 (database.py)
├── models.py       # 模型层：定义 SQLModel 数据库表结构
├── repositories/   # 仓储层：封装数据库 CRUD 操作
├── schemas/        # 架构层：Pydantic 请求与响应模型
├── services/       # 业务逻辑层：处理复杂的业务逻辑（如搜索、BMR计算）
└── app.py          # 应用入口
```

## 🚀 快速开始

### 1. 安装依赖

推荐使用 `uv` 进行快速安装：

```bash
uv sync
```

### 2. 环境配置

创建并编辑 `config.yaml`：

```yaml
database:
  url: "postgresql://user:password@localhost:5432/lose_weight"

llm:
  api_key: "your_openai_api_key"
  base_url: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"
```

### 3. 运行服务

```bash
uv run uvicorn src.app:app --reload
```

访问 `http://127.0.0.1:8000/docs` 查看交互式 API 文档。

## 🔍 语义搜索说明

系统使用 **Milvus** 作为向量存储中心，通过 **DashScope (Qwen)** 的嵌入模型将食物描述转换为高维向量。通过余弦相似度实现中英文跨语言的食物检索，支持文本搜索和图片识别搜索。

## 🧪 代码检查

在提交代码前，请运行以下命令进行 lint 和格式化：

```bash
uv run ruff check .
uv run ruff format .
```
