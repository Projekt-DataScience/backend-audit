from pydantic import BaseModel

class LPAQuestionDAO(BaseModel):
    question: str
    description: str
    category_id: int
    layer_id: int
    group_id: int