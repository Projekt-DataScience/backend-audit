from typing import List, Union
from pydantic import BaseModel

from dao.lpa_answer import LPAAnswerDAO

class GetAuditDAO(BaseModel):
    id: int = None
    due_date: str = None
    complete_datetime: str = None
    duration: int = None
    recurrent_audit: bool = None

    created_by_user: dict = None
    audited_user: dict = None
    auditor: dict = None
    assigned_group: dict = None
    assigned_layer: dict = None

    questions: List = None
    answers: List = None


class SpontanousAudit(BaseModel):
    due_date: str
    auditor: int
    assigned_group: int
    assigned_layer: int
    question_count: int


class CreatedSpontanousAudit(BaseModel):
    id: int = None
    due_date: str = None
    duration: int = None
    recurrent_audit: bool = None
    created_by_user_id: int = None
    audited_user_id: int = None
    auditor: int = None
    assigned_group: int = None
    assigned_layer: int = None
    question_count: int = None
    questions: list = []


class UpdateAuditDAO(BaseModel):
    due_date: str
    auditor: int
    assigned_group: int
    assigned_layer: int


class AnswerDAO(BaseModel):
    question_id: int
    answer_reason_id: Union[int, None]
    answer: int
    comment: str


class AuditDurationDAO(BaseModel):
    context: str
    duration: int


class CompleteAuditDAO(BaseModel):
    audited_user_id: int = None
    answers: List[AnswerDAO]
    durations: List[AuditDurationDAO]


class AuditAnswersDAO(BaseModel):
    audit_id: int
    answers: List[LPAAnswerDAO] = []