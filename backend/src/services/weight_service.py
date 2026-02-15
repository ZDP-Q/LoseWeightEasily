from typing import List, Optional

from ..models import WeightRecord
from ..repositories.weight_repository import WeightRepository
from ..schemas.weight import WeightCreate, WeightUpdate


class WeightService:
    def __init__(self, repository: WeightRepository):
        self.repo = repository

    def create_record(self, record_in: WeightCreate) -> WeightRecord:
        db_record = WeightRecord.model_validate(record_in)
        return self.repo.create_record(db_record)

    def get_records(self, limit: int = 100) -> List[WeightRecord]:
        return self.repo.get_records(limit)

    def get_record_by_id(self, record_id: int) -> Optional[WeightRecord]:
        return self.repo.get_record_by_id(record_id)

    def update_record(
        self, record_id: int, update_data: WeightUpdate
    ) -> Optional[WeightRecord]:
        record = self.repo.get_record_by_id(record_id)
        if not record:
            return None
        data = update_data.model_dump(exclude_unset=True)
        return self.repo.update_record(record, data)

    def delete_record(self, record_id: int) -> bool:
        record = self.repo.get_record_by_id(record_id)
        if not record:
            return False
        self.repo.delete_record(record)
        return True
