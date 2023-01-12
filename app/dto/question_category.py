from pydantic import BaseModel

class QuestionCategory(BaseModel):
    category_name: str

class QuestionCategoryWithId(BaseModel):
    id: int
    category_name: str