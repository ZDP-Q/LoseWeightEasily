from typing import List, Optional
from ..repositories.weight_repository import WeightRepository
from ..models import WeightRecord


class WeightService:
    def __init__(self, repository: WeightRepository):
        self.repo = repository

    def get_weight_history(self, user_id: int) -> List[WeightRecord]:
        return self.repo.get_weights(user_id)

    def get_records(self, user_id: int, limit: int = 1) -> List[WeightRecord]:
        return self.repo.get_weights(user_id, limit=limit)

    def record_weight(
        self, weight: float, user_id: int, notes: Optional[str] = ""
    ) -> WeightRecord:
        return self.repo.add_weight(weight, user_id, notes)

    def delete_record(self, record_id: int, user_id: int) -> bool:
        return self.repo.delete_weight(record_id, user_id)
