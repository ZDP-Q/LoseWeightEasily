# 贡献指南

感谢您对本项目的关注！欢迎提交 Issue 和 Pull Request。

## 开发环境设置

1. 克隆项目

```bash
git clone https://github.com/ZDP-Q/LossWeightEasily.git
cd LossWeightEasily
```

2. 安装开发依赖

```bash
uv sync --all-extras
```

3. 运行测试

```bash
uv run pytest
```

## 代码规范

本项目使用 [Ruff](https://github.com/astral-sh/ruff) 进行代码检查和格式化。

```bash
# 检查代码
uv run ruff check .

# 格式化代码
uv run ruff format .
```

## 提交规范

提交信息请遵循以下格式：

```
<type>: <description>

[optional body]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码风格（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

示例：
```
feat: 添加食物收藏功能
fix: 修复中文搜索结果排序问题
docs: 更新 API 文档
```

## Pull Request 流程

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加某功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 问题反馈

如果您发现 bug 或有功能建议，请创建 Issue：

1. 搜索是否已有相关 Issue
2. 使用清晰的标题描述问题
3. 提供详细的复现步骤（如果是 bug）
4. 附上相关的错误信息或截图

## 许可证

提交代码即表示您同意将代码以 MIT 许可证发布。
