import datetime

from dateutil.relativedelta import relativedelta
from typing import List, Union
from fastapi import APIRouter, Header
from sqlalchemy import and_

from db import dbm
from helpers.auth import validate_authorization
from dao.analytics import SingleGroupAnalytics, AuditAnalytics

from backend_db_lib.models import Group, LPAAudit, LPAAnswer, User

router = APIRouter(
    prefix="/api/audit/analytics",
    tags=["lpa_anyltics"],
    responses={404: {"description": "Not found"}},
)


@router.get("/groups")
def get_analytics_by_group(authorization: Union[str, None] = Header(default=None)) -> List[SingleGroupAnalytics]:
    payload = validate_authorization(authorization)
    company_id = payload.get("company_id")

    with dbm.create_session() as session:
        # Gruppen der Company abfragen
        groups = session.query(Group).filter(
            Group.company_id == company_id).all()

        response = []
        for group in groups:
            # Get all Audits of this group
            audits = session.query(LPAAudit).filter(
                LPAAudit.assigned_group_id == group.id).all()

            # Get answers of audit
            total_answers = 0
            total_green = 0
            total_yellow = 0
            total_red = 0
            for audit in audits:
                answers = session.query(LPAAnswer).filter(
                    LPAAnswer.audit_id == audit.id).all()
                total_answers += len(answers)
                for answer in answers:
                    if answer.answer == 0:
                        total_green += 1
                    elif answer.answer == 1:
                        total_yellow += 1
                    elif answer.answer == 2:
                        total_red += 1

            # Calculating the percentages
            if total_answers != 0:
                result = SingleGroupAnalytics(
                    group_name=group.group_name,
                    percent_green=total_green / total_answers,
                    percent_yellow=total_yellow / total_answers,
                    percent_red=total_red / total_answers,
                )
            else:
                result = SingleGroupAnalytics(
                    group_name=group.group_name,
                    percent_green=0,
                    percent_yellow=0,
                    percent_red=0,
                )

            response.append(result)

    return response


@router.get("/audits")
def get_audit_analytics(authorization: Union[str, None] = Header(default=None)) -> List[AuditAnalytics]:
    payload = validate_authorization(authorization)
    company_id = payload.get("company_id")

    to_datetime = datetime.date.today()
    from_datetime = datetime.datetime.now() - relativedelta(months=6)

    with dbm.create_session() as session:
        # audits = session.query(LPAAudit, User).join(
        #    User, and_(LPAAudit.created_by_user_id == User.id)).all()
        audits = session.query(LPAAudit).all()

    return audits
