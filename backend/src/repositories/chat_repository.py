from typing import List
from sqlmodel import Session, select, desc, delete
from ..models import ChatMessage


class ChatRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_history(self, user_id: int, limit: int | None = 20) -> List[ChatMessage]:
        """获取用户的聊天历史记录，按时间倒序排列。"""
        statement = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(desc(ChatMessage.timestamp))
        )
        if limit is not None:
            statement = statement.limit(limit)
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

    def add_messages(self, user_id: int, messages: List[tuple[str, str]]) -> None:
        """批量保存聊天记录，单事务提交。"""
        if not messages:
            return

        records = [
            ChatMessage(user_id=user_id, role=role, content=content)
            for role, content in messages
        ]
        self.session.add_all(records)
        self.session.commit()

    def clear_history(self, user_id: int):
        """清除用户的所有聊天历史记录。"""
        statement = delete(ChatMessage).where(ChatMessage.user_id == user_id)
        self.session.exec(statement)
        self.session.commit()
