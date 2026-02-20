from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Session, select

from ..models import FoodRecognition


class FoodRecognitionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_recognition_log(
        self,
        user_id: Optional[int],
        image_path: str,
        food_name: str,
        calories: float,
        verification_status: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> FoodRecognition:
        log = FoodRecognition(
            user_id=user_id,
            image_path=image_path,
            food_name=food_name,
            calories=calories,
            verification_status=verification_status,
            reason=reason,
            timestamp=datetime.now(timezone.utc),
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def get_logs_by_user(self, user_id: int, limit: int = 10) -> List[FoodRecognition]:
        statement = (
            select(FoodRecognition)
            .where(FoodRecognition.user_id == user_id)
            .order_by(FoodRecognition.timestamp.desc())
            .limit(limit)
        )
        return list(self.session.exec(statement).all())
