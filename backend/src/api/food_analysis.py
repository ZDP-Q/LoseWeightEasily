from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from ..schemas.food_analysis import FoodRecognitionResponse
from ..services.food_analysis_service import FoodAnalysisService

router = APIRouter(prefix="/food-analysis", tags=["food-analysis"])


def get_food_analysis_service(request: Request) -> FoodAnalysisService:
    return FoodAnalysisService(agent=request.app.state.agent)


@router.post("/recognize", response_model=FoodRecognitionResponse)
async def recognize_food(
    file: UploadFile = File(...),
    service: FoodAnalysisService = Depends(get_food_analysis_service),
):
    try:
        image_data = await file.read()
        return await service.analyze_food_image(image_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
