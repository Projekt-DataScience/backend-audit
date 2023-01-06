import datetime
from dateutil.relativedelta import relativedelta
import random
from typing import List
from collections import defaultdict

from db import dbm
from backend_db_lib.models import LPAAnswer, LPAAudit
from dao.analytics import AuditAnalytics


def calculate_audits_analytics(session, audits: List[LPAAudit]) -> List[AuditAnalytics]:
    audit_months = defaultdict(lambda: [])

    # TODO: fix complete_datetime null
    # Use actual month from complete_datetime instead of artifical created
    num_audits = len(audits)
    if num_audits == 0:
        return []

    now = datetime.datetime.now()
    months = []
    for _ in range(0, 6):
        month = (now - relativedelta(months=_)).month
        months.append(month)

    print("============================================")
    print(months)

    random.seed(42)
    for month in months:
        audit_months[month] = random.choices(
            audits, k=random.randint(1, num_audits))

    response = []
    for month in audit_months.keys():
        audits = audit_months[month]

        total_answers = 0
        total_green = 0
        total_yellow = 0
        total_red = 0

        year = 0
        for audit in audits:
            year = (datetime.datetime.now() - relativedelta(months=month)).year
            answers = session.query(LPAAnswer).filter(
                LPAAnswer.audit_id == audit.id).all()
            for answer in answers:
                total_answers += 1
                if answer.answer == 0:
                    total_green += 1
                elif answer.answer == 1:
                    total_yellow += 1
                elif answer.answer == 2:
                    total_red += 1

        if total_answers == 0:
            total_answers = 1

        month_audit_analytics = AuditAnalytics(
            month=month,
            year=year,

            num_green=total_green,
            num_yellow=total_yellow,
            num_red=total_red,

            percent_green=round(total_green / total_answers * 100, 2),
            percent_yellow=round(total_yellow / total_answers * 100, 2),
            percent_red=round(total_red / total_answers * 100, 2),
        )

        response.append(month_audit_analytics)

    return response
