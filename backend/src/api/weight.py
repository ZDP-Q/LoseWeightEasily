from fastapi import APIRouter, Depends
from typing import List
from sqlmodel import Session
from ..schemas.weight import WeightCreate, WeightRead
from ..services.weight_service import WeightService
from ..core.database import get_session

router = APIRouter(prefix="/weight", tags=["weight"])


def get_weight_service(session: Session = Depends(get_session)) -> WeightService:
    return WeightService(session)


@router.post("", response_model=WeightRead)
def create_weight_record(
    data: WeightCreate, service: WeightService = Depends(get_weight_service)
):
    return service.create_record(data)


@router.get("", response_model=List[WeightRead])
def get_weight_records(
    limit: int = 100, service: WeightService = Depends(get_weight_service)
):
    return service.get_records(limit)
