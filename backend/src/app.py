import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlmodel import Session
from fastapi.middleware.cors import CORSMiddleware

from .api import food, meal_plan, user, weight, food_analysis, chat
from .core.config import get_settings
from .core.logging import setup_logging
from .core.security import verify_api_key

settings = get_settings()
# 立即初始化日志配置
setup_logging()
logger = logging.getLogger("loseweight.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 初始化数据库、Milvus、LoseWeightAgent

    # Initialize DB
    from .core.database import init_db, engine

    init_db()

    # 初始化向量检索服务
    try:
        from LoseWeightAgent.src.services.embedding_service import EmbeddingService
        from LoseWeightAgent.src.services.milvus_manager import MilvusManager
        from LoseWeightAgent.src.services.food_search import FoodSearchService

        embedding_service = EmbeddingService(
            api_key=settings.llm.api_key,
            model=settings.embedding.model,
            dimension=settings.embedding.dimension,
        )

        milvus_manager = MilvusManager(
            host=settings.milvus.host,
            port=settings.milvus.port,
            collection_name=settings.milvus.collection,
            vector_dim=settings.embedding.dimension,
        )

        app.state.food_search = FoodSearchService(
            embedding_service=embedding_service,
            milvus_manager=milvus_manager,
        )
        logger.info(
            "食物检索服务初始化成功 (Milvus=%s:%d, model=%s)",
            settings.milvus.host,
            settings.milvus.port,
            settings.embedding.model,
        )
    except Exception as e:
        app.state.food_search = None
        logger.error("食物检索服务初始化失败: %s", e)

    # 初始化 LoseWeightAgent（AI 功能核心）
    try:
        from LoseWeightAgent.src.agent import LoseWeightAgent

        agent = LoseWeightAgent(
            api_key=settings.llm.api_key,
            base_url=settings.llm.base_url,
            model=settings.llm.model,
            milvus_host=settings.milvus.host,
            milvus_port=settings.milvus.port,
            milvus_collection=settings.milvus.collection,
            embedding_model=settings.embedding.model,
            embedding_dimension=settings.embedding.dimension,
            session_factory=lambda: Session(engine),
        )
        app.state.agent = agent
        logger.info("LoseWeightAgent 初始化成功 (model=%s)", settings.llm.model)
    except Exception as e:
        app.state.agent = None
        logger.error("LoseWeightAgent 初始化失败: %s", e)

    yield

    # Shutdown
    logger.info("正在关闭应用...")


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
