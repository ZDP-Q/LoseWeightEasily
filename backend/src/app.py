import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import faiss
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

from .api import food, meal_plan, user, weight, food_analysis, chat
from .core.config import get_settings
from .core.logging import setup_logging
from .core.security import verify_api_key

settings = get_settings()
logger = logging.getLogger("loseweight.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 初始化日志、数据库、模型和索引
    setup_logging()
    logger.info("正在加载 Embedding 模型和 FAISS 索引...")

    # Initialize DB
    from .core.database import init_db

    init_db()

    # Load SentenceTransformer
    app.state.embedding_model = SentenceTransformer(settings.embedding.model)

    # Load FAISS index and metadata (使用 JSON 代替 pickle)
    index_path = settings.index.index_path
    metadata_path = settings.index.metadata_path

    if index_path.exists() and metadata_path.exists():
        app.state.food_index = faiss.read_index(str(index_path))
        app.state.food_metadata = _load_metadata(metadata_path)
        logger.info("FAISS 索引加载成功。")
    else:
        app.state.food_index = None
        app.state.food_metadata = None
        logger.warning(
            "找不到索引文件 %s 或 %s。搜索功能将不可用。",
            index_path,
            metadata_path,
        )

    # 初始化 LoseWeightAgent（AI 功能核心）
    try:
        from LoseWeightAgent.src.agent import LoseWeightAgent

        agent = LoseWeightAgent(
            api_key=settings.llm.api_key,
            base_url=settings.llm.base_url,
            model=settings.llm.model,
        )
        app.state.agent = agent
        logger.info("LoseWeightAgent 初始化成功 (model=%s)", settings.llm.model)
    except Exception as e:
        app.state.agent = None
        logger.error("LoseWeightAgent 初始化失败: %s", e)

    yield

    # Shutdown
    logger.info("正在关闭应用...")


def _load_metadata(metadata_path: Path) -> list[int]:
    """安全加载 metadata，优先使用 JSON，兼容旧版 pickle。"""
    json_path = metadata_path.with_suffix(".json")

    # 优先读 JSON
    if json_path.exists():
        with open(json_path, encoding="utf-8") as f:
            return json.load(f)

    # 兼容旧版 pickle（加日志警告）
    import pickle  # noqa: S403

    logger.warning(
        "使用 pickle 加载 metadata (%s)，建议迁移到 JSON 格式。", metadata_path
    )
    with open(metadata_path, "rb") as f:
        data = pickle.load(f)  # noqa: S301

    # 自动创建 JSON 副本以供下次使用
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        logger.info("已自动将 metadata 转换为 JSON 格式: %s", json_path)
    except Exception:
        logger.warning("自动转换 JSON 失败，将在下次启动时重试。")

    return data


app = FastAPI(
    title="LoseWeightEasily API",
    description="重构后的减肥助手后端接口",
    version="3.0.0",
    lifespan=lifespan,
    dependencies=[Depends(verify_api_key)],
)

# CORS 中间件配置（从配置文件读取允许的源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(food.router)
app.include_router(meal_plan.router)
app.include_router(weight.router)
app.include_router(user.router)
app.include_router(food_analysis.router)
app.include_router(chat.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy", "version": "3.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
