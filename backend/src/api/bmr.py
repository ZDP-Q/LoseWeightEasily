from fastapi import APIRouter
from ..schemas.bmr import BMRInput, BMRResult
from ..services.bmr_service import BMRService

router = APIRouter(prefix="/calculate", tags=["calculation"])


@router.post("/bmr", response_model=BMRResult)
def calculate_bmr(data: BMRInput):
    bmr = BMRService.calculate_bmr(
        weight=data.weight_kg, height=data.height_cm, age=data.age, gender=data.gender
    )
    tdee = BMRService.get_all_tdee_levels(bmr)
    return BMRResult(bmr=bmr, tdee=tdee)
