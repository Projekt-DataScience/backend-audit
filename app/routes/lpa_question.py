from typing import Union

from fastapi import APIRouter, HTTPException, Header

from backend_db_lib.models import LPAQuestion, LPAQuestionCategory, Layer, Group, AuditQuestionAssociation, LPAAudit, LPAAnswer
from dto.lpa_question import LPAQuestionDAO, LPAQuestionAnswersDAO
from db import dbm
from helpers.lpa_question import fill_question
from helpers.lpa_answer import fill_answer
from helpers.auth import validate_authorization

router = APIRouter(
    prefix="/api/audit/lpa_question",
    tags=["lpa_question"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
@router.get("/")
def get_lpa_questions(authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    with dbm.create_session() as session:
        questions = session.query(LPAQuestion).all()

        for question in questions:
            fill_question(session, question)

    return questions


@router.get("/audit/{audit_id}")
def get_questions_of_audit(audit_id: int, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)

    with dbm.create_session() as session:
        audit = session.query(LPAAudit).get(audit_id)
        if audit is None:
            raise HTTPException(404, "Audit not found.")

        result = session.query(AuditQuestionAssociation, LPAQuestion).filter(
            AuditQuestionAssociation.audit_id == audit_id
        ).filter(
            LPAQuestion.id == AuditQuestionAssociation.question_id
        ).all()

    return [r["LPAQuestion"] for r in result]


@router.get("/{id}")
def get_lpa_question(id: int, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)

    with dbm.create_session() as session:
        question = session.query(LPAQuestion).get(id)
        if question is None:
            raise HTTPException(status_code=404)

        question = fill_question(session, question)

    return question


@router.post("")
@router.post("/")
def create_lpa_question(lpa_question: LPAQuestionDAO, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)

    with dbm.create_session() as session:
        category = session.query(LPAQuestionCategory).get(
            lpa_question.category_id)
        if category is None:
            raise HTTPException(
                status_code=404, detail="LPA Question Category not found")

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
def update_lpa_question(lpa_question: LPAQuestionDAO, id: int, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)

    with dbm.create_session() as session:
        category = session.query(LPAQuestionCategory).get(
            lpa_question.category_id)
        if category is None:
            raise HTTPException(
                status_code=404, detail="LPA Question Category not found")

        question = session.query(LPAQuestion).get(id)
        if question is None:
            raise HTTPException(
                status_code=404, detail="LPA Question not found")

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
def delete_question(id: int, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    
    with dbm.create_session() as session:
        question = session.query(LPAQuestion).get(id)
        if question is None:
            raise HTTPException(
                status_code=404, detail="LPA Question not found")

        session.delete(question)
        session.commit()

    return id

@router.get("/answers/{question_id}", response_model=LPAQuestionAnswersDAO)
def get_question_answers(question_id: int, last: int, authorization: Union[str, None] = Header(default=None)) -> LPAQuestionAnswersDAO:
    payload = validate_authorization(authorization)
    with dbm.create_session() as session:
        green = session.query(LPAAnswer).filter(LPAAnswer.question_id == question_id, LPAAnswer.answer == 0).order_by(LPAAnswer.id.desc()).limit(last).all()
        yellow = session.query(LPAAnswer).filter(LPAAnswer.question_id == question_id, LPAAnswer.answer == 1).order_by(LPAAnswer.id.desc()).limit(last).all()
        red = session.query(LPAAnswer).filter(LPAAnswer.question_id == question_id, LPAAnswer.answer == 2).order_by(LPAAnswer.id.desc()).limit(last).all()

        green_response = []
        for g in green:
            green_response.append(fill_answer(g))

        red_response = []
        for r in red:
            red_response.append(fill_answer(r))

        yellow_response = []
        for y in yellow:
            yellow_response.append(fill_answer(y))

    return LPAQuestionAnswersDAO(
        green=green_response,
        yellow=yellow_response,
        red=red_response,
    )