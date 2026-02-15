from typing import Optional
from sqlmodel import Session, select
from ..models import User
from ..schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_user(self) -> Optional[User]:
        # 简化逻辑：获取数据库中的第一个用户（单用户应用）
        statement = select(User)
        return self.session.exec(statement).first()

    def create_user(self, user_in: UserCreate) -> User:
        db_user = User.model_validate(user_in)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def update_user(self, user_update: UserUpdate) -> Optional[User]:
        db_user = self.get_user()
        if not db_user:
            return None

        user_data = user_update.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)

        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user
