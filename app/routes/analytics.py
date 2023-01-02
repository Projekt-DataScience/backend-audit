from typing import List, Union

from fastapi import APIRouter, HTTPException, Header

from backend_db_lib.models import LPAQuestion, LPAAnswer, LPAAudit, User, Layer, Group
from db import dbm
from helpers.auth import validate_authorization
import json
from sqlalchemy.ext.serializer import loads, dumps
from helpers.lpa_question import fill_question
from sqlalchemy import or_, and_


router = APIRouter(
    prefix="/api/audit/analytics",
    tags=["lpa_anyltics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/questions")
def get_questions_analytics(authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    usercompany = payload.get("company_id")

    with dbm.create_session() as session:
        
        response = []

        allquestions = session.query(LPAQuestion).join(Layer, and_(LPAQuestion.layer_id == Layer.id)).join(Group, and_(LPAQuestion.group_id == Group.id)).filter(or_(Layer.company_id == usercompany, Group.company_id == usercompany)).all()
        for question in allquestions:
            green = session.query(LPAAnswer).where(LPAAnswer.question_id == question.id).filter(LPAAnswer.answer == 0).count()
            yellow = session.query(LPAAnswer).where(LPAAnswer.question_id == question.id).filter(LPAAnswer.answer == 1).count()
            red = session.query(LPAAnswer).where(LPAAnswer.question_id == question.id).filter(LPAAnswer.answer == 2).count()
            total = green + yellow + red
            if total == 0:
                total = 1
            percent_green = round(green / total *100, 2)
            percent_yellow = round(yellow / total * 100, 2)
            percent_red = round(red / total * 100, 2)
            response.append({
            "question": fill_question(session, question), "num_green": green, "num_yellow": yellow, "num_red": red, "percent_green": percent_green, "percent_yellow": percent_yellow, "percent_red": percent_red
            })

    return response