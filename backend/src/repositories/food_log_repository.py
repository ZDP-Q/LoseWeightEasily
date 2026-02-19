from datetime import datetime, time, timedelta, timezone
from typing import List

from sqlmodel import Session, select, and_

from ..models import FoodLog


class FoodLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_log(self, user_id: int, food_name: str, calories: float) -> FoodLog:
        log = FoodLog(user_id=user_id, food_name=food_name, calories=calories)
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def get_logs_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime) -> List[FoodLog]:
        statement = select(FoodLog).where(
            and_(
                FoodLog.user_id == user_id,
                FoodLog.timestamp >= start_date,
                FoodLog.timestamp < end_date
            )
        ).order_by(FoodLog.timestamp.asc())
        return self.session.exec(statement).all()

    def get_today_logs(self, user_id: int) -> List[FoodLog]:
        now = datetime.now(timezone.utc)
        start_of_day = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
        end_of_day = start_of_day + timedelta(days=1)
        return self.get_logs_by_date_range(user_id, start_of_day, end_of_day)
