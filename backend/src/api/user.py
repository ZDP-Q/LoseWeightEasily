from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..schemas.user import UserCreate, UserRead, UserUpdate
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..core.database import get_session

router = APIRouter(prefix="/user", tags=["user"])


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(UserRepository(session))


@router.get("", response_model=UserRead)
def get_user(service: UserService = Depends(get_user_service)):
    user = service.get_user()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserRead)
def create_user(data: UserCreate, service: UserService = Depends(get_user_service)):
    existing_user = service.get_user()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return service.create_user(data)


@router.patch("", response_model=UserRead)
def update_user(data: UserUpdate, service: UserService = Depends(get_user_service)):
    user = service.update_user(data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
