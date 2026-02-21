# 第一阶段：构建依赖
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# 设置工作目录
WORKDIR /app

# 设置环境变量，启用字节码预编译并跳过开发依赖
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 复制依赖定义并同步虚拟环境
# 注意：backend 目录下有 LoseWeightAgent 目录，uv 会自动处理 pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv 
    --mount=type=bind,source=uv.lock,target=uv.lock 
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml 
    uv sync --frozen --no-install-project --no-dev

# 第二阶段：运行时
FROM python:3.12-slim-bookworm

# 设置工作目录
WORKDIR /app

# 复制从构建阶段生成的虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 将虚拟环境路径添加到 PATH
ENV PATH="/app/.venv/bin:$PATH"

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统库（针对 psycopg2 和 Pillow 的运行时库）
# 注意：使用 -binary 版 psycopg2 可减少此处的 libpq 依赖需求
RUN apt-get update && apt-get install -y --no-install-recommends 
    libpq5 
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 复制后端源码和核心子模块（LoseWeightAgent）
# 注意：根据项目结构，源码在 src，LoseWeightAgent 在 LoseWeightAgent
COPY src/ /app/src/
COPY LoseWeightAgent/ /app/LoseWeightAgent/
COPY data/ /app/data/
# 复制配置文件模板（用户可在运行时挂载实际的 config.yaml）
COPY config.yaml.example /app/config.yaml

# 暴露端口
EXPOSE 16666

# 运行 FastAPI 应用
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "16666"]
