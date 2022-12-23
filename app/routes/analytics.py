from typing import List, Union

from fastapi import APIRouter, HTTPException, Header

from backend_db_lib.models import LPAQuestion, LPAAnswer, LPAAudit, User
from db import dbm
from helpers.auth import validate_authorization
import json
from sqlalchemy.ext.serializer import loads, dumps


router = APIRouter(
    prefix="/api/audit/analytics",
    tags=["lpa_anyltics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/questions/{a_id}")
def get_lpa_answer_reasons(a_id: int,authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    usercompany = payload.get("company_id")

    with dbm.create_session() as session:
        usersofcompany = session.query(User.id).where(User.company_id == usercompany).all()
        auditsforcompany = []
        for user in usersofcompany:
            auditsforcompany.append(session.query(LPAAudit.id).where(LPAAudit.created_by_user_id == user.id).all())
        questionsandanswersforaudits = []
        auditsforcompany.pop(0)
        # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        # print(auditsforcompany)
        # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        
        for i in range(len(auditsforcompany)):
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            print(auditsforcompany[i])
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            # questionsandanswersforaudits.append(session.query(LPAAnswer).where(LPAAnswer.audit_id == audit["id"]).all())

    return auditsforcompany