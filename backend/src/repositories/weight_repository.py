from typing import List, Optional
from sqlmodel import Session, select
from ..models import WeightRecord


class WeightRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_weights(
        self, user_id: int, limit: Optional[int] = None
    ) -> List[WeightRecord]:
        """获取指定用户的所有体重记录。"""
        statement = (
            select(WeightRecord)
            .where(WeightRecord.user_id == user_id)
            .order_by(WeightRecord.recorded_at.desc())
        )
        if limit:
            statement = statement.limit(limit)
        return list(self.session.exec(statement).all())

    def add_weight(
        self, weight: float, user_id: int, notes: Optional[str] = ""
    ) -> WeightRecord:
        """为特定用户增加体重记录。"""
        record = WeightRecord(weight_kg=weight, user_id=user_id, notes=notes)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def delete_weight(self, record_id: int, user_id: int) -> bool:
        """删除特定用户的体重记录（安全验证）。"""
        statement = select(WeightRecord).where(
            WeightRecord.id == record_id, WeightRecord.user_id == user_id
        )
        record = self.session.exec(statement).first()
        if not record:
            return False
        self.session.delete(record)
        self.session.commit()
        return True
