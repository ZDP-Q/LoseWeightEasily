from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..schemas.weight import WeightCreate, WeightRead
from ..services.weight_service import WeightService
from ..repositories.weight_repository import WeightRepository
from ..core.database import get_session
from ..core.security import get_current_user
from ..models import User

router = APIRouter(prefix="/weight", tags=["weight"])


def get_weight_service(session: Session = Depends(get_session)) -> WeightService:
    return WeightService(WeightRepository(session))


@router.get("", response_model=list[WeightRead])
def get_weights(
    current_user: User = Depends(get_current_user),
    service: WeightService = Depends(get_weight_service),
):
    return service.get_weight_history(current_user.id)


@router.post("", response_model=WeightRead)
def add_weight(
    data: WeightCreate,
    current_user: User = Depends(get_current_user),
    service: WeightService = Depends(get_weight_service),
):
    return service.record_weight(data.weight_kg, current_user.id, data.notes)


@router.delete("/{record_id}")
def delete_weight(
    record_id: int,
    current_user: User = Depends(get_current_user),
    service: WeightService = Depends(get_weight_service),
):
    success = service.delete_record(record_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Weight record not found")
    return {"status": "success"}
