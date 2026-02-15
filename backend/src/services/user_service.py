from typing import Optional

from ..models import User
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repo = repository

    def get_user(self) -> Optional[User]:
        return self.repo.get_first_user()

    def create_user(self, user_in: UserCreate) -> User:
        db_user = User.model_validate(user_in)
        return self.repo.create_user(db_user)

    def update_user(self, user_update: UserUpdate) -> Optional[User]:
        db_user = self.repo.get_first_user()
        if not db_user:
            return None

        user_data = user_update.model_dump(exclude_unset=True)
        return self.repo.update_user(db_user, user_data)
