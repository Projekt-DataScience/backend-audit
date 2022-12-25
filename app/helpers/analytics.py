import datetime

from typing import List
from collections import defaultdict

from db import dbm
from backend_db_lib.models import LPAAnswer, LPAAudit
from dao.analytics import AuditAnalytics


def calculate_audits_analytics(session, audits: List[LPAAudit]) -> List[AuditAnalytics]:
    audit_months = defaultdict(lambda: [])
    for audit, user in audits:
        audit_months[audit.complete_datetime.month].append(audit)

    response = []
    for month in audit_months.keys():
        audits = audit_months[month]

        total_answers = 0
        total_green = 0
        total_yellow = 0
        total_red = 0

        year = 0
        for audit in audits:
            year = audit.complete_datetime.year
            answers = session.query(LPAAnswer).filter(LPAAnswer.audit_id == audit.id).all()
            for answer in answers:
                total_answers += 1
                if answer.answer == 0:
                    total_green += 1
                elif answer.answer == 1:
                    total_yellow += 1
                elif answer.answer == 2:
                    total_red += 1

        month_audit_analytics = AuditAnalytics(
            month=month,
            year=year,
            
            num_green=total_green,
            num_yellow=total_yellow,
            num_red=total_red,

            percent_green=total_green / total_answers,
            percent_yellow=total_yellow / total_answers,
            percent_red=total_red / total_answers,
        )

        response.append(month_audit_analytics)

    return response