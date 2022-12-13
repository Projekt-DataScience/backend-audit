from typing import List

from fastapi import APIRouter, HTTPException

from backend_db_lib.models import LPAAnswerReason
from dao.lpa_answer import LPAAnswerReasonDAO
from db import dbm

router = APIRouter(
    prefix="/api/audit/lpa_answer",
    tags=["lpa_answer"],
    responses={404: {"description": "Not found"}},
)


@router.get("/reason")
def get_lpa_answer_reasons() -> List[LPAAnswerReason]:
    with dbm.create_session() as session:
        answer_reasons = session.query(LPAAnswerReason).all()

    return answer_reasons


@router.post("/reason")
def create_lpa_answer_reason(answer: LPAAnswerReasonDAO):
    with dbm.create_session() as session:
        answer = LPAAnswerReason(
            description=answer.description
        )

        session.add(answer)
        session.flush()
        session.commit()
        session.refresh(answer)

    return answer


@router.post("/reason/{id}")
def update_lpa_answer_reason(answer: LPAAnswerReasonDAO, id: int):
    with dbm.create_session() as session:
        answer_reason = session.query(LPAAnswerReason).get(id)
        if answer_reason is None:
            raise HTTPException(
                status_code=404, detail="LPA Answer Reason not found")

        answer_reason.description = answer.description

        session.add(answer_reason)
        session.flush()
        session.commit()
        session.refresh(answer_reason)

    return answer_reason


@router.post("/reason/delete/{id}")
def delete_lpa_answer_reason(id: int):
    with dbm.create_session() as session:
        answer_reason = session.query(LPAAnswerReason).get(id)
        if answer_reason is None:
            raise HTTPException(
                status_code=404, detail="LPA Answer Reason not found")

        session.delete(answer_reason)
        session.commit()

    return id
