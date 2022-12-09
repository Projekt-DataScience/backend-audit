import uvicorn
from fastapi import FastAPI, Header, HTTPException

from backend_db_lib.models import base, LPAAudit, LPAQuestionCategory
from backend_db_lib.manager import DatabaseManager

from dao.QuestionCategory import QuestionCategory, QuestionCategoryWithId

DATABASE_URL = "postgresql://backendgang:backendgang@db:8010/backend"

dbm = DatabaseManager(base, DATABASE_URL)
app = FastAPI()

@app.get("/healthcheck")
def healthcheck():
    return { "Status": "Up" }

@app.get("/question_category")
def get_question_categories():
    with dbm.create_session() as session:
        question_categories = session.query(LPAQuestionCategory).all()

    return question_categories

@app.post("/question_category")
def create_question_category(question_category: QuestionCategory):
    with dbm.create_session() as session:
        c = LPAQuestionCategory(category_name=question_category.category_name)
        session.add(c)
        session.flush()
        session.commit()
        session.refresh(c)

    return c

@app.post("/question_category/{id}")
def update_question_category(question_category: QuestionCategory, id):
    with dbm.create_session() as session:
        c = session.query(LPAQuestionCategory).get(id)
        c.category_name = question_category.category_name
        session.add(c)
        session.flush()
        session.commit()
        session.refresh(c)

    return c

@app.post("/question_category/delete/{id}")
def update_question_category(id):
    with dbm.create_session() as session:
        c = session.query(LPAQuestionCategory).get(id)
        
        if not c:
            raise HTTPException(status_code=404, detail="LPA Question Category not found")

        session.delete(c)
        session.commit()

    return id

@app.get("/audit")
def get_audits(authorization: str | None = Header(default=None)):
    pass


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)