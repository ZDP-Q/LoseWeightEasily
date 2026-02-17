from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..core.database import get_session
from sqlmodel import Session

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(UserRepository(session))


@router.post("", response_model=ChatResponse)
async def chat_with_coach(
    request_data: ChatRequest,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    agent = request.app.state.agent
    if not agent:
        raise HTTPException(status_code=503, detail="AI Agent 未初始化")

    user_info = ""
    try:
        user = user_service.get_user()
        if user and user.tdee:
            user_info = (
                f"用户信息：姓名 {user.name}, 体重 {user.initial_weight_kg}kg, "
                f"身高 {user.height_cm}cm, 年龄 {user.age}, TDEE {user.tdee:.0f}kcal。"
            )
    except Exception:
        pass

    try:
        reply = await agent.get_guidance_direct(
            question=request_data.message, user_info=user_info
        )
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
