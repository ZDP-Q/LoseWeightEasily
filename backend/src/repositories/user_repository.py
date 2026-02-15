from typing import Optional

from sqlmodel import Session, select

from ..models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_first_user(self) -> Optional[User]:
        """获取数据库中的第一个用户（单用户应用）。"""
        statement = select(User)
        return self.session.exec(statement).first()

    def create_user(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_user(self, user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
