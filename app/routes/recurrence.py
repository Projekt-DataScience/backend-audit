import random

from fastapi import APIRouter, HTTPException

from dao.recurrence import RecurrenceDAO
from backend_db_lib.models import LPAAuditRecurrence, User, Group, Layer, LPAAudit, AuditQuestionAssociation, LPAQuestion, LPAQuestionCategory, LPAAnswerReason, LPAAnswer
from db import dbm, RECURRENCE_TYPES, frontend_recurrence_value_to_backend_recurrence_value, backend_to_frontend_recurrence_value, reccurrence_value_to_date

router = APIRouter(
    prefix="/planned",
    tags=["planned"],
    responses={404: {"description": "Not found"}},
)

@router.get("")
def get_rhytms():
    with dbm.create_session() as session:
        recurrences = session.query(LPAAuditRecurrence).all()

    for recurrence in recurrences:
        recurrence.values = backend_to_frontend_recurrence_value(recurrence.type, recurrence.value)

    return recurrences

@router.get("/types")
def get_recurrence_types():
    return RECURRENCE_TYPES.TYPES

@router.get("/generate_audits")
def create_recurrent_audits():
    created_audits = []
    with dbm.create_session() as session:
        recurrences = session.query(LPAAuditRecurrence).all()
        
        for recurrence in recurrences:
            question_count = recurrence.question_count
            dates = reccurrence_value_to_date(recurrence.type, recurrence.value)
            
            for date in dates:
                audit = session.query(LPAAudit).filter(
                    LPAAudit.assigned_layer_id == recurrence.layer_id,
                    LPAAudit.assigned_group_id == recurrence.group_id,
                    LPAAudit.auditor_user_id == recurrence.auditor_id,
                    LPAAudit.due_date == date,
                )
                if audit.count() > 0:
                    continue

                audit = LPAAudit(
                    due_date=date,
                    auditor_user_id=recurrence.auditor_id,
                    created_by_user_id=recurrence.auditor_id,
                    assigned_group_id=recurrence.group_id,
                    assigned_layer_id=recurrence.layer_id,
                    recurrent_audit=True,
                )
                session.add(audit)
                session.flush()
                session.refresh(audit)

                questions = session.query(LPAQuestion).all()
                rand_questions = random.choices(questions, k=question_count)

                for question in rand_questions:
                    association = AuditQuestionAssociation(
                        audit_id=audit.id,
                        question_id=question.id
                    )
                    session.add(association)

                created_audits.append(audit.id)

                session.commit()

    return created_audits

@router.get("/values/{type}")
def get_recurrence_values(type: str):
    if type not in RECURRENCE_TYPES.TYPES:
        raise HTTPException(status_code=404, detail="Recurrence type is invalid")

    return RECURRENCE_TYPES.VALUES[type]

@router.get("/{id}")
def get_rhytm(id: int):
    with dbm.create_session() as session:
        recurrence = session.query(LPAAuditRecurrence).get(id)
        if recurrence is None:
            raise HTTPException(status_code=404)

    recurrence.values = backend_to_frontend_recurrence_value(recurrence.type, recurrence.value)

    return recurrence

@router.post("")
def create_rhytm(recurrence: RecurrenceDAO):
    with dbm.create_session() as session:
        auditor = session.query(User).get(recurrence.auditor_id)
        if auditor is None:
            raise HTTPException(status_code=404, detail="Auditor not found")

        group = session.query(Group).get(recurrence.group_id)
        if group is None:
            raise HTTPException(status_code=404, detail="Group not found")

        layer = session.query(Layer).get(recurrence.layer_id)
        if layer is None:
            raise HTTPException(status_code=404, detail="Layer not found")

        if recurrence.recurrence_type not in RECURRENCE_TYPES.TYPES:
            raise HTTPException(status_code=404, detail="Recurrence type is invalid")

        if recurrence.question_count <= 0:
            raise HTTPException(status_code=400, detail="Question count is invalid")
        
        value = frontend_recurrence_value_to_backend_recurrence_value(
            recurrence.recurrence_type,
            recurrence.values
        )

        r = LPAAuditRecurrence(
            auditor_id=recurrence.auditor_id,
            group_id=recurrence.group_id,
            layer_id=recurrence.layer_id,
            type=recurrence.recurrence_type,
            question_count=recurrence.question_count,
            value=value
        )

        session.add(r)
        session.flush()
        session.commit()
        session.refresh(r)

    response = RecurrenceDAO(
        id=r.id,
        auditor_id=r.auditor_id,
        group_id=r.group_id,
        layer_id=r.layer_id,
        question_count=r.question_count,
        recurrence_type=r.type,
        values=backend_to_frontend_recurrence_value(r.type, r.value)
    )

    return response
