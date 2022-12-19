from pydantic import BaseModel

from typing import List

class RecurrenceDAO(BaseModel):
    id: int
    auditor_id: int
    group_id: int
    layer_id: int
    question_count: int
    recurrence_type: str
    values: List[str]


class ResponseRecurrenceDAO(BaseModel):
    id: int
    auditor: dict
    group: dict
    layer: dict
    question_count: int
    recurrence_type: str
    values: List[str]