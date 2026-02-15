import pickle
import faiss
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer

from .core.config import get_settings
from .core.database import init_db
from .api import bmr, food, meal_plan, weight, user

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models and indices
    print("正在加载 Embedding 模型和 FAISS 索引...")

    # Initialize DB
    init_db()

    # Load SentenceTransformer
    app.state.embedding_model = SentenceTransformer(settings.embedding.model)

    # Load FAISS index and metadata
    index_path = settings.index.index_path
    metadata_path = settings.index.metadata_path

    if index_path.exists() and metadata_path.exists():
        app.state.food_index = faiss.read_index(str(index_path))
        with open(metadata_path, "rb") as f:
            app.state.food_metadata = pickle.load(f)
        print("FAISS 索引加载成功。")
    else:
        app.state.food_index = None
        app.state.food_metadata = None
        print(
            f"警告: 找不到索引文件 {index_path} 或 {metadata_path}。搜索功能将不可用。"
        )

    yield

    # Shutdown: Clean up if necessary
    print("正在关闭应用...")


app = FastAPI(
    title="LoseWeightEasily API",
    description="重构后的减肥助手后端接口",
    version="2.0.0",
    lifespan=lifespan,
)

# Include Routers
app.include_router(bmr.router)
app.include_router(food.router)
app.include_router(meal_plan.router)
app.include_router(weight.router)
app.include_router(user.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
