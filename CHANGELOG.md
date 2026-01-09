# Changelog

本文档记录项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.2.0] - 2026-01-09

### 新增
- 项目重构为标准 Python 包结构
- 添加命令行工具 `loss-weight`
- 添加完整的 API 文档
- 添加单元测试框架
- 添加配置管理模块，支持环境变量
- 添加 MIT 许可证

### 变更
- 代码模块化重构
  - `database.py` - 数据库管理
  - `search.py` - FAISS 搜索引擎
  - `query.py` - 查询接口
  - `config.py` - 配置管理
  - `cli.py` - 命令行接口
- 更新项目依赖配置
- 优化文档结构

### 修复
- 改进错误处理和用户提示

## [0.1.0] - 2024-12-18

### 新增
- 初始版本发布
- 基于 FAISS 的向量语义搜索
- 支持中英文跨语言查询
- SQLite 数据库存储
- USDA FoodData Central 数据导入
- 交互式命令行查询界面
