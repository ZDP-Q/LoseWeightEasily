from typing import List
from sqlmodel import Session, select
from ..models import WeightRecord
from ..schemas.weight import WeightCreate

class WeightService:
    def __init__(self, session: Session):
        self.session = session

    def create_record(self, record_in: WeightCreate) -> WeightRecord:
        db_record = WeightRecord.model_validate(record_in)
        self.session.add(db_record)
        self.session.commit()
        self.session.refresh(db_record)
        return db_record

    def get_records(self, limit: int = 100) -> List[WeightRecord]:
        statement = select(WeightRecord).order_by(WeightRecord.recorded_at.desc()).limit(limit)
        return self.session.exec(statement).all()
