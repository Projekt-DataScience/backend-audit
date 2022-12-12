from fastapi import APIRouter, HTTPException

from backend_db_lib.models import LPAQuestion, LPAQuestionCategory, Layer, Group
from dao.lpa_question import LPAQuestionDAO
from db import dbm
from helpers.lpa_question import fill_question

router = APIRouter(
    prefix="/api/audit/lpa_question",
    tags=["lpa_question"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def get_lpa_questions():
    with dbm.create_session() as session:
        questions = session.query(LPAQuestion).all()

        for question in questions:
            fill_question(session, question)

    return questions


@router.get("/{id}")
def get_lpa_question(id: int):
    with dbm.create_session() as session:
        question = session.query(LPAQuestion).get(id)
        if question is None:
            raise HTTPException(status_code=404)

        question = fill_question(session, question)

    return question


@router.post("")
def create_lpa_question(lpa_question: LPAQuestionDAO):
    with dbm.create_session() as session:
        category = session.query(LPAQuestionCategory).get(lpa_question.category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="LPA Question Category not found")

        layer = session.query(Layer).get(lpa_question.layer_id)
        if layer is None:
            raise HTTPException(status_code=404, detail="Layer not found")

        group = session.query(Group).get(lpa_question.group_id)
        if group is None:
            raise HTTPException(status_code=404, detail="Group not found")

        question = LPAQuestion(
            question=lpa_question.question,
            description=lpa_question.description,
            category_id=lpa_question.category_id,
            layer_id=lpa_question.layer_id,
            group_id=lpa_question.group_id
        )

        session.add(question)
        session.flush()
        session.commit()
        session.refresh(question)

        question = fill_question(session, question)

    return question


@router.post("/{id}")
def update_lpa_question(lpa_question: LPAQuestionDAO, id: int):
    with dbm.create_session() as session:
        category = session.query(LPAQuestionCategory).get(lpa_question.category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="LPA Question Category not found")

        question = session.query(LPAQuestion).get(id)
        if question is None:
            raise HTTPException(status_code=404, detail="LPA Question not found")

        layer = session.query(Layer).get(lpa_question.layer_id)
        if layer is None:
            raise HTTPException(status_code=404, detail="Layer not found")

        group = session.query(Group).get(lpa_question.group_id)
        if group is None:
            raise HTTPException(status_code=404, detail="Group not found")

        question.question = lpa_question.question,
        question.description = lpa_question.description,
        question.category_id = lpa_question.category_id
        question.layer_id = lpa_question.layer_id
        question.group_id = lpa_question.group_id

        session.add(question)
        session.flush()
        session.commit()
        session.refresh(question)

        question = fill_question(session, question)

    return question


@router.post("/delete/{id}")
def delete_question(id: int):
    with dbm.create_session() as session:
        question = session.query(LPAQuestion).get(id)
        if question is None:
            raise HTTPException(status_code=404, detail="LPA Question not found")

        session.delete(question)
        session.commit()

    return id
