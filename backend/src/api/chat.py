import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session

from ..core.database import get_session
from ..repositories.user_repository import UserRepository
from ..services.user_service import UserService

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(UserRepository(session))


def _build_user_info(user_service: UserService) -> str:
    """构建用户信息上下文字符串。"""
    try:
        user = user_service.get_user()
        if user and user.tdee:
            return (
                f"用户信息：姓名 {user.name}, 体重 {user.initial_weight_kg}kg, "
                f"身高 {user.height_cm}cm, 年龄 {user.age}, "
                f"TDEE {user.tdee:.0f}kcal, "
                f"目标体重 {user.target_weight_kg}kg。"
            )
    except Exception:
        pass
    return ""


@router.post("", response_model=ChatResponse)
async def chat_with_coach(
    request_data: ChatRequest,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    """非流式聊天端点（向后兼容）。"""
    agent = request.app.state.agent
    if not agent:
        raise HTTPException(status_code=503, detail="AI Agent 未初始化")

    user_info = _build_user_info(user_service)

    try:
        reply = await agent.get_guidance_direct(
            question=request_data.message, user_info=user_info
        )
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(
    request_data: ChatRequest,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    """SSE 流式聊天端点。

    返回 text/event-stream，事件类型:
    - event: text      → 文本 chunk
    - event: action_result → Action 执行结果 JSON
    - event: done       → 流结束
    """
    agent = request.app.state.agent
    if not agent:
        raise HTTPException(status_code=503, detail="AI Agent 未初始化")

    user_info = _build_user_info(user_service)

    async def event_generator():
        try:
            async for event in agent.chat_stream(
                message=request_data.message, user_info=user_info
            ):
                event_type = event.get("event", "text")
                data = event.get("data", "")

                if event_type == "action_result":
                    data = json.dumps(data, ensure_ascii=False)
                elif event_type == "done":
                    data = ""

                yield f"event: {event_type}\ndata: {data}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"
        finally:
            yield "event: done\ndata: \n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
