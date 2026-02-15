from typing import List, Optional

from sqlmodel import Session, select

from ..models import WeightRecord


class WeightRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_record(self, record: WeightRecord) -> WeightRecord:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def get_records(self, limit: int = 100) -> List[WeightRecord]:
        statement = (
            select(WeightRecord).order_by(WeightRecord.recorded_at.desc()).limit(limit)
        )
        return list(self.session.exec(statement).all())

    def get_record_by_id(self, record_id: int) -> Optional[WeightRecord]:
        statement = select(WeightRecord).where(WeightRecord.id == record_id)
        return self.session.exec(statement).first()

    def update_record(self, record: WeightRecord, data: dict) -> WeightRecord:
        for key, value in data.items():
            setattr(record, key, value)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def delete_record(self, record: WeightRecord) -> None:
        self.session.delete(record)
        self.session.commit()
