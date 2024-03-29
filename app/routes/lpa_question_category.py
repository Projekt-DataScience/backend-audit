from typing import Union

from fastapi import APIRouter, HTTPException, Header

from backend_db_lib.models import LPAQuestionCategory
from dto.question_category import QuestionCategory
from db import dbm
from helpers.auth import validate_authorization

router = APIRouter(
    prefix="/api/audit/lpa_question_category",
    tags=["lpa_question_category"],
    responses={404: {"description": "Not found"}},
)


@router.get("/question_category")
def get_question_categories(authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)

    with dbm.create_session() as session:
        question_categories = session.query(LPAQuestionCategory).all()

    return question_categories


@router.get("/question_category/{id}")
def get_question_category_by_id(id: int, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)

    with dbm.create_session() as session:
        question_categorie = session.query(LPAQuestionCategory).get(id)
        if question_categorie is None:
            raise HTTPException(
                status_code=404, detail="LPA Question Category not found")

    return question_categorie


@router.post("/question_category")
def create_question_category(question_category: QuestionCategory, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)

    with dbm.create_session() as session:
        c = LPAQuestionCategory(category_name=question_category.category_name)
        session.add(c)
        session.flush()
        session.commit()
        session.refresh(c)

    return c


@router.post("/question_category/{id}")
def update_question_category(question_category: QuestionCategory, id, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)

    with dbm.create_session() as session:
        c = session.query(LPAQuestionCategory).get(id)
        c.category_name = question_category.category_name
        session.add(c)
        session.flush()
        session.commit()
        session.refresh(c)

    return c


@router.post("/question_category/delete/{id}")
def delete_question_category(id: int, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)

    with dbm.create_session() as session:
        c = session.query(LPAQuestionCategory).get(id)

        if not c:
            raise HTTPException(
                status_code=404, detail="LPA Question Category not found")

        session.delete(c)
        session.commit()

    return id
