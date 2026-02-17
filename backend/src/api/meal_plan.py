from fastapi import APIRouter, Depends, HTTPException, Request
from ..schemas.meal_plan import MealPlanRequest, MealPlanResponse
from ..services.meal_planner_service import MealPlanError, MealPlannerService

router = APIRouter(prefix="/meal-plan", tags=["meal-plan"])


def get_meal_planner_service(request: Request) -> MealPlannerService:
    return MealPlannerService(agent=request.app.state.agent)


@router.post("", response_model=MealPlanResponse)
async def generate_meal_plan(
    data: MealPlanRequest,
    service: MealPlannerService = Depends(get_meal_planner_service),
):
    try:
        return await service.generate_plan(
            ingredients=data.ingredients,
            preferences=data.preferences,
            restrictions=data.dietary_restrictions,
            goal=data.goal,
            target_calories=data.target_calories,
        )
    except MealPlanError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
