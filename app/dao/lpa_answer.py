from pydantic import BaseModel

from dao.lpa_question import LPAQuestionDAO

class LPAAnswerReasonDAO(BaseModel):
    description: str

class LPAAnswerDAO(BaseModel):
    id: int
    answer: str
    comment: str
    
    reason: LPAAnswerReasonDAO

    audit_id: int
    question_id: int
