from typing import List
from sqlmodel import Session, select, desc
from ..models import ChatMessage

class ChatRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_history(self, user_id: int, limit: int = 20) -> List[ChatMessage]:
        """获取用户的聊天历史记录，按时间倒序排列。"""
        statement = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(desc(ChatMessage.timestamp))
            .limit(limit)
        )
        # 获取后反转，使返回结果按时间正序排列
        messages = self.session.exec(statement).all()
        return list(reversed(messages))

    def add_message(self, user_id: int, role: str, content: str) -> ChatMessage:
        """保存一条新的聊天记录。"""
        message = ChatMessage(user_id=user_id, role=role, content=content)
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def clear_history(self, user_id: int):
        """清除用户的所有聊天历史记录。"""
        statement = select(ChatMessage).where(ChatMessage.user_id == user_id)
        messages = self.session.exec(statement).all()
        for msg in messages:
            self.session.delete(msg)
        self.session.commit()
