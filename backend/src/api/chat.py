import json
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session

from ..core.database import get_session
from ..models import ChatMessage
from ..repositories.user_repository import UserRepository
from ..repositories.weight_repository import WeightRepository
from ..repositories.chat_repository import ChatRepository
from ..services.user_service import UserService
from ..services.weight_service import WeightService

logger = logging.getLogger("loseweight.api.chat")

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(UserRepository(session))


def get_weight_service(session: Session = Depends(get_session)) -> WeightService:
    return WeightService(WeightRepository(session))


def get_chat_repo(session: Session = Depends(get_session)) -> ChatRepository:
    return ChatRepository(session)


def _build_user_info(user_service: UserService, weight_service: WeightService) -> str:
    """构建用户信息上下文字符串。"""
    try:
        user = user_service.get_user()
        if user and user.tdee:
            # 获取最新体重记录
            latest_records = weight_service.get_records(limit=1)
            current_weight = latest_records[0].weight_kg if latest_records else user.initial_weight_kg
            
            return (
                f"用户信息：姓名 {user.name}, 当前体重 {current_weight}kg, "
                f"身高 {user.height_cm}cm, 年龄 {user.age}, "
                f"TDEE {user.tdee:.0f}kcal, "
                f"目标体重 {user.target_weight_kg}kg。"
            )
    except Exception:
        pass
    return ""


@router.get("/history", response_model=List[ChatMessage])
async def get_chat_history(
    user_service: UserService = Depends(get_user_service),
    chat_repo: ChatRepository = Depends(get_chat_repo),
):
    """获取当前用户的聊天历史记录。"""
    user = user_service.get_user()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return chat_repo.get_history(user.id, limit=50)


@router.post("", response_model=ChatResponse)
async def chat_with_coach(
    request_data: ChatRequest,
    request: Request,
    user_service: UserService = Depends(get_user_service),
    weight_service: WeightService = Depends(get_weight_service),
    chat_repo: ChatRepository = Depends(get_chat_repo),
):
    """非流式聊天端点（支持历史记录和持久化）。"""
    agent = request.app.state.agent
    if not agent:
        raise HTTPException(status_code=503, detail="AI Agent 未初始化")

    user = user_service.get_user()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user_info = _build_user_info(user_service, weight_service)
    
    # 获取历史记录并转换为 OpenAI 格式
    history_objs = chat_repo.get_history(user.id, limit=10)
    history = [{"role": h.role, "content": h.content} for h in history_objs]

    try:
        reply = await agent.get_guidance_direct(
            question=request_data.message, user_info=user_info, history=history
        )
        
        # 异步保存到数据库
        chat_repo.add_message(user.id, "user", request_data.message)
        chat_repo.add_message(user.id, "assistant", reply)
        
        return ChatResponse(reply=reply)
    except Exception as e:
        logger.error(f"非流式对话出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(
    request_data: ChatRequest,
    request: Request,
    user_service: UserService = Depends(get_user_service),
    weight_service: WeightService = Depends(get_weight_service),
    chat_repo: ChatRepository = Depends(get_chat_repo),
):
    """SSE 流式聊天端点（带记忆持久化）。"""
    agent = request.app.state.agent
    if not agent:
        raise HTTPException(status_code=503, detail="AI Agent 未初始化")

    user = user_service.get_user()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user_info = _build_user_info(user_service, weight_service)
    
    # 获取历史记录
    history_objs = chat_repo.get_history(user.id, limit=10)
    history = [{"role": h.role, "content": h.content} for h in history_objs]

    async def event_generator():
        full_reply = ""
        try:
            async for event in agent.chat_stream(
                message=request_data.message, user_info=user_info, history=history
            ):
                event_type = event.get("event", "text")
                data = event.get("data", "")

                if event_type == "text":
                    full_reply += data
                elif event_type == "action_result":
                    data = json.dumps(data, ensure_ascii=False)
                elif event_type == "usage":
                    data = json.dumps(data, ensure_ascii=False)
                elif event_type == "done":
                    data = ""
                
                yield f"event: {event_type}\ndata: {data}\n\n"
            
            # 对话结束后保存记录
            chat_repo.add_message(user.id, "user", request_data.message)
            if full_reply:
                chat_repo.add_message(user.id, "assistant", full_reply)
                
        except Exception as e:
            logger.error(f"流式响应生成出错: {e}")
            yield f"event: error\ndata: {str(e)}\n\n"
        finally:
            yield "event: done\ndata: \n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Content-Type": "text/event-stream",
        },
    )
