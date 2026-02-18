# LoseWeightEasily 🍎

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flutter Version](https://img.shields.io/badge/flutter-3.11+-blue.svg)](https://flutter.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个基于 AI 和语义搜索的现代化减重助手。本项目已从传统的桌面端应用重构为高性能的 **Client-Server** 架构，提供基于 FastAPI 的强大后端和基于 Flutter 的精美移动端应用。

## ✨ 核心特性

- 🔍 **智能语义搜索**：基于 **Milvus** 向量数据库和 **DashScope** 多模态嵌入模型，支持跨语言（中英）搜索 USDA 食物营养数据。
- ⚖️ **体重趋势追踪**：可视化记录每日体重变化，生成动态趋势图表。
- 🔥 **代谢精准计算**：计算 BMR（基础代谢率）和 TDEE（每日总消耗），辅助制定减脂计划。
- 🍽️ **AI 食谱规划**：集成 OpenAI API，根据现有食材和营养需求智能生成一日三餐建议。
- 🎨 **现代 UI/UX**：Flutter 移动端采用 Material 3 设计规范、Poppins 字体以及 Glassmorphism（毛玻璃）视觉风格。
- ⚡ **高性能架构**：FastAPI + SQLModel (PostgreSQL) 后端，支持高并发和高效的向量检索。

## 🏗️ 架构概览

项目采用前后端分离架构：
- **后端 (Backend)**: 提供 RESTful API，处理数据持久化、语义搜索算法及 AI 逻辑。
- **移动端 (Mobile App)**: 提供跨平台的用户交互界面，利用 `Provider` 进行响应式状态管理。

## 📁 目录结构

```text
LoseWeightEasily/
├── backend/                # FastAPI 后端项目
│   ├── src/
│   │   ├── api/            # 路由定义 (BMR, Food, Meal Plan, Weight)
│   │   ├── core/           # 核心配置与数据库连接
│   │   ├── models.py       # SQLModel 数据库模型
│   │   ├── schemas/        # Pydantic 验证架构
│   │   ├── services/       # 业务逻辑层
│   │   └── app.py          # 应用入口
│   ├── data/               # USDA 食物数据集
│   └── pyproject.toml      # uv 依赖管理
├── mobile_app/             # Flutter 移动端项目
│   ├── lib/
│   │   ├── models/         # 数据模型
│   │   ├── screens/        # 各功能模块页面
│   │   ├── services/       # API 请求封装
│   │   ├── utils/          # 主题与配色常量
│   │   └── widgets/        # 自定义 UI 组件 (如 GlassCard)
│   └── pubspec.yaml        # Flutter 依赖管理
└── GEMINI.md               # AI 开发上下文与指令
```

## 🚀 快速开始

### 1. 后端配置 (Backend)

确保已安装 [uv](https://github.com/astral-sh/uv)。

```bash
cd backend
# 复制并配置环境变量/配置文件
cp config.yaml.example config.yaml
# 安装依赖并启动服务
uv run uvicorn src.app:app --reload
```
后端默认运行在 `http://127.0.0.1:8000`。API 文档可通过 `/docs` 访问。

### 2. 移动端运行 (Mobile App)

确保已安装 Flutter SDK 3.11.0+。

```bash
cd mobile_app
flutter pub get
flutter run
```
*注意：在 Android 模拟器中运行，请确保 API 基础路径配置为 `http://10.0.2.2:8000`。*

## 🛠️ 技术栈

- **后端**: [FastAPI](https://fastapi.tiangolo.com/), [SQLModel](https://sqlmodel.tiangolo.com/), [PostgreSQL](https://www.postgresql.org/), [Milvus](https://milvus.io/), [DashScope](https://help.aliyun.com/product/2399481.html)
- **前端**: [Flutter](https://flutter.dev/), [Provider](https://pub.dev/packages/provider), [fl_chart](https://pub.dev/packages/fl_chart)
- **工具**: [uv](https://github.com/astral-sh/uv), [Ruff](https://github.com/astral-sh/ruff)

## 📊 数据来源

食物营养数据基于 [USDA FoodData Central](https://fdc.nal.usda.gov/) 2025-12-18 版本。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
