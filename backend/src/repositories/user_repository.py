from typing import List, Optional

from sqlmodel import Session, select

from ..models import Ingredient, User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        statement = select(User).where(User.id == user_id)
        return self.session.exec(statement).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户（用于登录）。"""
        statement = select(User).where(User.username == username)
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

    def get_ingredients(self, user_id: int) -> List[Ingredient]:
        """获取用户的食材库存。"""
        statement = select(Ingredient).where(Ingredient.user_id == user_id)
        return list(self.session.exec(statement).all())

    def add_ingredient(self, user_id: int, name: str) -> Ingredient:
        """为用户增加食材记录。"""
        ingredient = Ingredient(name=name, user_id=user_id)
        self.session.add(ingredient)
        self.session.commit()
        self.session.refresh(ingredient)
        return ingredient
