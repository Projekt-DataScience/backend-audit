from pydantic import BaseModel

class LPAQuestionDAO(BaseModel):
    question: str
    description: str
    category_id: int