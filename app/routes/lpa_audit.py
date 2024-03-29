import random
from typing import List, Union
import requests

from datetime import datetime

from fastapi import APIRouter, HTTPException, Header

from backend_db_lib.models import LPAAudit, User, Group, Layer, LPAQuestion, AuditQuestionAssociation, LPAAuditDuration, \
    LPAAnswer, LPAAnswerReason, LPAQuestionCategory
from helpers.auth import validate_authorization
from dto.lpa_audit import SpontanousAudit, CreatedSpontanousAudit, UpdateAuditDAO, CompleteAuditDAO, GetAuditDAO, \
    AuditAnswersDAO
from dto.lpa_question import CreatedLPAQuestionDAO
from helpers.audit_date_parser import parse_audit_due_date, convert_audit_due_date
from helpers.audit import fill_audit, choose_questions_for_audit
from helpers.lpa_answer import fill_answer
from db import dbm
from settings import settings

router = APIRouter(
    prefix="/api/audit/lpa_audit",
    tags=["lpa_audit"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
def get_all_audits(authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    with dbm.create_session() as session:
        audits = session.query(LPAAudit).all()

        response_audits = []
        for audit in audits:
            response_audits.append(fill_audit(session, audit))

    return response_audits


@router.get("/complete")
def get_all_complete_audits(authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    with dbm.create_session() as session:
        audits = session.query(LPAAudit).filter(
            LPAAudit.duration != None
        ).all()

        response_audits = []
        for audit in audits:
            filled_audit = fill_audit(session, audit)
            if len(filled_audit.answers) > 0:
                response_audits.append(filled_audit)

    return response_audits


@router.get("/{id}")
def get_audit(id: int, authorization: Union[str, None] = Header(default=None)) -> GetAuditDAO:
    payload = validate_authorization(authorization)
    with dbm.create_session() as session:
        audit = session.query(LPAAudit).get(id)

        if audit is None:
            raise HTTPException(status_code=404, detail="Audit not found")

        response_audit = fill_audit(session, audit)

    return response_audit


@router.get("/open/{user_id}")
def get_audits_of_user(user_id: int, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    with dbm.create_session() as session:
        user = session.query(User).get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        layer_id = user.layer_id
        group_id = user.group_id

        if (layer_id is not None) and (group_id is not None):
            audits = session.query(LPAAudit).filter_by(
                assigned_group_id=group_id,
                assigned_layer_id=layer_id,
            )
        elif layer_id is None:
            audits = session.query(LPAAudit).filter_by(
                assigned_group_id=group_id,
            )
        elif group_id is None:
            audits = session.query(LPAAudit).filter_by(
                assigned_layer_id=layer_id,
            )

        audits = audits.filter(
            LPAAudit.due_date >= datetime.now(),
            LPAAudit.duration == None
        )

        response_audits = []
        for audit in audits.all():
            response_audits.append(fill_audit(session, audit))

        return response_audits


@router.post("")
def create_spontanous_lpa_audit(audit: SpontanousAudit,
                                authorization: Union[str, None] = Header(default=None)) -> CreatedSpontanousAudit:
    payload = validate_authorization(authorization)
    create_by_user_id = payload["user_id"]

    with dbm.create_session() as session:
        auditor = session.query(User).get(audit.auditor)
        if auditor is None:
            raise HTTPException(status_code=404, detail="Auditor not found")

        created_by_user = session.query(User).get(create_by_user_id)

        assigned_group = session.query(Group).get(audit.assigned_group)
        if assigned_group is None:
            raise HTTPException(status_code=404, detail="Group not found")

        assigned_layer = session.query(Layer).get(audit.assigned_group)
        if assigned_layer is None:
            raise HTTPException(status_code=404, detail="Layer not found")

        # For parsing strings with this format: 2022-10-22T00:00:00
        due_date = parse_audit_due_date(audit.due_date)

        lpa_audit = LPAAudit(
            due_date=due_date,
            duration=None,  # We have not completted the audit yet
            recurrent_audit=False,  # Because this is spontanously created
            created_by_user_id=created_by_user.id,
            audited_user_id=None,  # Not audited yet
            auditor_user_id=auditor.id,
            assigned_group_id=assigned_group.id,
            assigned_layer_id=assigned_layer.id,
        )

        session.add(lpa_audit)
        session.flush()
        session.commit()
        session.refresh(lpa_audit)

        created_audit = CreatedSpontanousAudit()
        created_audit.id = lpa_audit.id
        created_audit.due_date = lpa_audit.due_date
        created_audit.duration = lpa_audit.duration
        created_audit.recurrent_audit = lpa_audit.recurrent_audit
        created_audit.created_by_user_id = lpa_audit.created_by_user_id
        created_audit.audited_user_id = lpa_audit.audited_user_id
        created_audit.auditor = lpa_audit.auditor_user_id
        created_audit.assigned_group = lpa_audit.assigned_group_id
        created_audit.assigned_layer = lpa_audit.assigned_layer_id
        created_audit.question_count = audit.question_count

        # Choosing random questions for audit
        all_questions = {x.id: x for x in session.query(LPAQuestion).filter_by(
            layer_id=assigned_layer.id,
            group_id=assigned_group.id,
        ).all()}

        algorithm = audit.algorithm
        if algorithm is None:
            algorithm = "weighted_sum"

        chosen_question = choose_questions_for_audit(session, all_questions, audit.question_count, lpa_audit, algorithm)
        created_audit.questions.extend(chosen_question)

        session.flush()
        session.commit()

    return created_audit


@router.post("/{id}")
def update_audit(audit: UpdateAuditDAO, id: int, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    with dbm.create_session() as session:
        a = session.query(LPAAudit).get(id)
    if a is None:
        raise HTTPException(status_code=404, detail="Audit not found")

    auditor = session.query(User).get(audit.auditor)
    if auditor is None:
        raise HTTPException(status_code=404, detail="Auditor not found")

    assigned_group = session.query(Group).get(audit.assigned_group)
    if assigned_group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    assigned_layer = session.query(Layer).get(audit.assigned_group)
    if assigned_layer is None:
        raise HTTPException(status_code=404, detail="Layer not found")

    a.auditor_user_id = auditor.id
    a.assigned_group_id = assigned_group.id
    a.assigned_layer_id = assigned_layer.id
    a.due_date = parse_audit_due_date(audit.due_date)

    session.add(a)
    session.flush()
    session.commit()
    session.refresh(a)

    return a


@router.post("/delete/{id}")
def delete_audit(id: int, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    with dbm.create_session() as session:
        audit = session.query(LPAAudit).get(id)
        if audit is None:
            raise HTTPException(status_code=404, detail="LPA Audit not found")

        session.delete(audit)
        session.commit()

    return id


@router.post("/complete/{id}")
def complete_audit(complete_audit: CompleteAuditDAO, id: int, authorization: Union[str, None] = Header(default=None)):
    print(authorization)
    payload = validate_authorization(authorization)
    with dbm.create_session() as session:
        audit = session.query(LPAAudit).get(id)
        if audit is None:
            raise HTTPException(status_code=404, detail="LPA Audit not found")

        if audit.duration is not None:
            raise HTTPException(
                status_code=400, detail="Audit already completed")

        audited = session.query(User).get(complete_audit.audited_user_id)
        if audited is None:
            raise HTTPException(
                status_code=404, detail="Audited user not found")
        audit.audited_user_id = audited.id

        for answer in complete_audit.answers:
            if answer.answer_reason_id is not None:
                answer_reason = session.query(
                    LPAAnswerReason).get(answer.answer_reason_id)
                if answer_reason is None:
                    raise HTTPException(
                        status_code=404, detail=f"Answer reason with ID {answer.answer_reason_id} not found")

            question = session.query(LPAQuestion).get(answer.question_id)
            if question is None:
                raise HTTPException(
                    status_code=404, detail=f"Question with ID {answer.question_id} not found")

            audit_answer = LPAAnswer(
                answer=answer.answer,
                comment=answer.comment,
                lpa_answer_reason_id=answer.answer_reason_id,
                audit_id=audit.id,
                question_id=answer.question_id,
            )
            session.add(audit_answer)

        duration_complete = 0
        for duration in complete_audit.durations:
            duration_complete += duration.duration
            audit_duration = LPAAuditDuration(
                audit_id=audit.id,
                context=duration.context,
                duration=duration.duration,
            )
            session.add(audit_duration)

        audit.duration = duration_complete
        audit.complete_datetime = datetime.now()
        session.add(audit)

        session.flush()
        session.commit()
        session.refresh(audit)

        # Create Response Answer
        response = requests.get(
            f"{settings.AUDIT_API_URL}/api/audit/lpa_audit/{id}",
            headers={"Authorization": authorization},
        )

    return response.json()


@router.get("/answers/{id}", response_model=AuditAnswersDAO)
def get_answers_of_audit(id: int, authorization: Union[str, None] = Header(default=None)) -> AuditAnswersDAO:
    token = validate_authorization(authorization)

    with dbm.create_session() as session:
        audit = session.query(LPAAudit).get(id)
        if audit is None:
            raise HTTPException(status_code=404, detail="Audit not found")

        answers = session.query(LPAAnswer).filter_by(
            audit_id=audit.id).all()

        audit_answers = AuditAnswersDAO(
            audit_id=audit.id,
            answers=[],
        )

        for answer in answers:
            audit_answer = fill_answer(answer)
            audit_answers.answers.append(audit_answer)

    return audit_answers
