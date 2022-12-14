from typing import List

from backend_db_lib.models import LPAAudit, Group, Layer, User, LPAAuditDuration
from backend_db_lib.models import AuditQuestionAssociation, LPAQuestion, LPAAnswer, LPAAnswerReason
from backend_db_lib.models import LPAQuestionCategory

from helpers.auth import get_user
from helpers.audit_date_parser import convert_audit_due_date

from dao.lpa_audit import GetAuditDAO


def get_questions_of_audit(session, audit_id: int) -> List[LPAQuestion]:
    questions = session.query(AuditQuestionAssociation).filter_by(
        audit_id=audit_id).all()
    question_ids = [question.question_id for question in questions]
    questions = []
    for id in question_ids:
        question = session.query(LPAQuestion).get(id)
        if question is not None:
            question.layer = session.query(Layer).get(question.layer_id)
            question.group = session.query(Group).get(question.group_id)
            question.category = session.query(
                LPAQuestionCategory).get(question.category_id)
            questions.append(question)

    return questions


def get_answers_of_audit(session, audit_id: int) -> List[LPAAnswer]:
    answers = session.query(LPAAnswer).filter_by(audit_id=audit_id).all()
    answer_ids = [answer.id for answer in answers]
    answers = []
    for id in answer_ids:
        answer = session.query(LPAAnswer).get(id)
        if answer.lpa_answer_reason_id is not None:
            answer.reason = session.query(LPAAnswerReason).get(
                answer.lpa_answer_reason_id)
        answers.append(answer)

    return answers


def get_durations_of_audit(session, audit_id: int) -> List[LPAAuditDuration]:
    durations = session.query(LPAAuditDuration).filter_by(
        audit_id=audit_id).all()
    duration_ids = [duration.id for duration in durations]
    durations = []
    for id in duration_ids:
        duration = session.query(LPAAuditDuration).get(id)
        durations.append(duration)

    return durations


def fill_audit(session, audit: LPAAudit) -> GetAuditDAO:
    """
    Adds assigned group, assigned layer, created by user, auditor, questions, audited user, questions,
    answers and durations to audit object
    :param audit:
    :return:
    """

    response_audit = GetAuditDAO()
    response_audit.id = audit.id
    response_audit.due_date = convert_audit_due_date(audit.due_date)
    if response_audit.complete_datetime is not None:
        response_audit.complete_datetime = convert_audit_due_date(
            audit.complete_datetime)
    response_audit.duration = audit.duration
    response_audit.recurrent_audit = audit.recurrent_audit

    response_audit.assigned_group = session.query(
        Group).get(audit.assigned_group_id)
    response_audit.assigned_layer = session.query(
        Layer).get(audit.assigned_layer_id)

    response_audit.questions = get_questions_of_audit(session, audit.id)
    response_audit.answers = get_answers_of_audit(session, audit.id)

    response_audit.created_by_user = get_user(
        session, audit.created_by_user_id)
    response_audit.auditor = get_user(session, audit.auditor_user_id)
    if audit.audited_user_id is not None:
        response_audit.audited_user = get_user(session, audit.audited_user_id)

    return response_audit
