import random

from fastapi import APIRouter, HTTPException

from backend_db_lib.models import LPAAudit, User, Group, Layer, LPAQuestion, AuditQuestionAssociation
from dao.lpa_audit import SpontanousAudit, CreatedSpontanousAudit, UpdateAuditDAO
from dao.lpa_question import CreatedLPAQuestionDAO
from helpers.audit_date_parser import parse_audit_due_date
from db import dbm


router = APIRouter(
    prefix="/lpa_audit",
    tags=["lpa_audit"],
    responses={404: {"description": "Not found"}},
)

@router.get("")
def get_all_audits():
    with dbm.create_session() as session:
        audits = session.query(LPAAudit).all()

    return audits

@router.get("/{id}")
def get_audit(id):
    with dbm.create_session() as session:
        audit = session.query(LPAAudit).get(id)
    
    if audit is None:
        raise HTTPException(status_code=404, detail="Audit not found")

    return audit

@router.post("/")
def create_spontanous_lpa_audit(audit: SpontanousAudit):   
    with dbm.create_session() as session:
        auditor = session.query(User).get(audit.auditor)
        if auditor is None:
            raise HTTPException(status_code=404, detail="Auditor not found")

        # TODO: Change created by with current logged in user
        created_by_user = session.query(User).get(audit.auditor)

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
            duration=None, # We have not completted the audit yet
            recurrent_audit=False, # Because this is spontanously created
            created_by_user_id=created_by_user.id,
            audited_user_id=None, # Not audited yet
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
        all_questions = session.query(LPAQuestion).filter_by(
            layer_id=assigned_layer.id,
            group_id=assigned_group.id,
        ).all()
        random_questions = random.choices(all_questions, k=audit.question_count)

        for question in random_questions:
            question_dao = CreatedLPAQuestionDAO(
                id=question.id,
                question=question.question,
                description=question.description,
                category_id=question.category_id,
                layer_id=question.layer_id,
                group_id=question.group_id,
            )
            created_audit.questions.append(question_dao)

            aq = AuditQuestionAssociation(
                audit_id=lpa_audit.id,
                question_id=question.id,
            )
            session.add(aq)
        
        session.flush()
        session.commit()

    return created_audit

@router.post("/{id}")
def update_audit(audit: UpdateAuditDAO, id):
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
def delete_audit(id: int):
    with dbm.create_session() as session:
        audit = session.query(LPAAudit).get(id)
        if audit is None:
            raise HTTPException(status_code=404, detail="LPA Audit not found")

        session.delete(audit)
        session.commit()

    return id