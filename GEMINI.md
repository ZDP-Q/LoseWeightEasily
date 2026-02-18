# Gemini Added Memories

- 你的回答必须使用中文！
- python项目使用uv管理，包管理以及代码运行必须使用uv命令。
- 完成python代码之后必须使用ruff检查和修复问题。
- 使用flutter开发完成之后需要进行静态检查、语法以及编码规范检查和编译测试，确保代码合规且正常运行。
- git提交必须遵循基本的规范，分门别类地提交，提交信息符合基本规范，且必须使用中文进行提交。
- **绝对不准运行任何名为 `main.py` 的文件**，无论它在哪个目录下。

---

# LoseWeightEasily 项目上下文

本项目是一个基于 **Client-Server** 架构的轻量级减重助手，旨在通过 AI 和语义搜索帮助用户管理饮食和体重。

## 🏗️ 架构概览

- **后端 (Backend):** 基于 **FastAPI** 的 RESTful API，采用分层架构 (Repository/Service/API)，运行在 Python 3.12+ 环境下。
- **前端 (Frontend):** 基于 **Flutter** 的移动端应用（Android/iOS）。
- **数据库:** **PostgreSQL**，用于存储用户信息、体重记录和核心业务数据。
- **搜索引擎:** 基于 **Milvus** 向量数据库和 **DashScope (Qwen)** 嵌入模型的语义搜索引擎。
- **AI 核心:** 自研 **LoseWeightAgent**，集成 LLM 进行智能对话、食谱规划和食物多模态分析。

## 📁 核心目录结构

- `backend/`: 后端源码。
  - `src/`: 核心业务逻辑。
    - `api/`: FastAPI 路由处理器。
    - `core/`: 核心配置、数据库连接、日志等基础组件。
    - `models/`: 数据库模型 (SQLModel)。
    - `repositories/`: 数据库访问层。
    - `schemas/`: Pydantic 数据验证模型。
    - `services/`: 业务服务层。
    - `app.py`: FastAPI 应用入口。
  - `LoseWeightAgent/`: AI 功能核心组件。
    - `src/agent.py`: Agent 主控逻辑。
    - `src/services/`: 包含 Milvus 管理、嵌入生成、食物检索等 AI 服务。
  - `data/`: 存储食物原始元数据 (`.json`)。
  - `config.yaml`: 项目配置文件。
- `mobile_app/`: Flutter 源码。
  - `lib/`: Dart 源代码。
    - `main.dart`: 应用入口。
    - `services/api_service.dart`: API 交互层。
    - `screens/`: 界面逻辑。
    - `models/`: 前端数据模型。

## 🚀 开发与运行

### 后端 (Backend)
1. **环境准备:** 进入 `backend` 目录，确保已安装 `uv`。
2. **安装依赖:** `uv sync`
3. **配置文件:** 复制 `config.yaml.example` 为 `config.yaml` 并填写 PostgreSQL 和 LLM API 配置。
4. **运行服务:** 
   ```bash
   cd backend
   uv run uvicorn src.app:app --reload
   ```
5. **代码规范:** 在提交前运行 `ruff check . --fix`。

### 前端 (Mobile App)
1. **安装依赖:** `flutter pub get`
2. **运行应用:**
   ```bash
   cd mobile_app
   flutter run
   ```
3. **注意事项:** Android 模拟器访问本地后端地址通常为 `http://10.0.2.2:8000`。

## 🔧 技术规范与约定

- **后端开发:** 
  - 严格遵守 `backend/src/models.py` 定义的 PostgreSQL Schema。
  - 使用 `SQLModel` 进行 ORM 操作。
  - 异步处理耗时操作（如 LLM 调用）。
- **前端开发:**
  - 保持 Material Design 设计风格。
  - 网络请求统一封装在 `ApiService` 中。
- **代码提交:** 
  - 必须使用中文编写 commit message。
  - 遵循 `feat:`, `fix:`, `docs:`, `refactor:` 等前缀规范。

## ⚠️ 关键禁令
- **禁止运行 `main.py`**: 该文件在项目重构后已废弃，且可能包含冲突逻辑。
- **禁止直接修改数据库 Schema**: 必须同步更新 `backend/src/models.py`。
