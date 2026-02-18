from fastapi import APIRouter, Depends, Request, UploadFile, File
from typing import Optional

from ..services.food_service import FoodService
from ..core.config import get_settings

from LoseWeightAgent.src.schemas import FoodNutritionSearchResult

router = APIRouter(prefix="/food", tags=["food"])
settings = get_settings()


def get_food_service(request: Request) -> FoodService:
    food_search = request.app.state.food_search
    if food_search is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="食物检索服务未初始化")
    return FoodService(food_search=food_search)


@router.get("/search", response_model=list[FoodNutritionSearchResult])
def search_food(
    query: str,
    limit: Optional[int] = None,
    service: FoodService = Depends(get_food_service),
):
    """通过文本搜索食物营养信息。"""
    search_limit = limit or settings.search.limit
    return service.search_by_text(query, search_limit)


@router.post("/image", response_model=list[FoodNutritionSearchResult])
async def search_food_by_image(
    file: UploadFile = File(...),
    limit: Optional[int] = None,
    service: FoodService = Depends(get_food_service),
):
    """通过上传食物图片搜索营养信息（多模态检索）。"""
    image_data = await file.read()

    # 从文件名推断格式
    filename = file.filename or "image.jpeg"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpeg"
    format_map = {"jpg": "jpeg", "png": "png", "webp": "webp", "bmp": "bmp"}
    image_format = format_map.get(ext, "jpeg")

    search_limit = limit or settings.search.limit
    return service.search_by_image(image_data, search_limit, image_format)
