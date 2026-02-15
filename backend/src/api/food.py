from fastapi import APIRouter, Depends, Request
from typing import List
from sqlmodel import Session
from ..schemas.food import FoodSearchResult
from ..services.food_service import FoodService
from ..core.database import get_session

router = APIRouter(prefix="/search", tags=["food"])


def get_food_service(
    request: Request, session: Session = Depends(get_session)
) -> FoodService:
    return FoodService(
        session=session,
        model=request.app.state.embedding_model,
        index=request.app.state.food_index,
        metadata=request.app.state.food_metadata,
    )


@router.get("", response_model=List[FoodSearchResult])
def search_foods(
    query: str, limit: int = 10, service: FoodService = Depends(get_food_service)
):
    return service.search_foods(query, limit)
