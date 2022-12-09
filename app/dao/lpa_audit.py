from typing import List
from pydantic import BaseModel

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