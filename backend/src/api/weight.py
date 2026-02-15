from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session
from ..schemas.weight import WeightCreate, WeightRead, WeightUpdate
from ..services.weight_service import WeightService
from ..repositories.weight_repository import WeightRepository
from ..core.database import get_session

router = APIRouter(prefix="/weight", tags=["weight"])


def get_weight_service(session: Session = Depends(get_session)) -> WeightService:
    return WeightService(WeightRepository(session))


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


@router.patch("/{record_id}", response_model=WeightRead)
def update_weight_record(
    record_id: int,
    data: WeightUpdate,
    service: WeightService = Depends(get_weight_service),
):
    record = service.update_record(record_id, data)
    if not record:
        raise HTTPException(status_code=404, detail="体重记录不存在")
    return record


@router.delete("/{record_id}")
def delete_weight_record(
    record_id: int, service: WeightService = Depends(get_weight_service)
):
    if not service.delete_record(record_id):
        raise HTTPException(status_code=404, detail="体重记录不存在")
    return {"detail": "删除成功"}
