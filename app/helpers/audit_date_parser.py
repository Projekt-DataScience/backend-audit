from datetime import datetime

def parse_audit_due_date(date: str):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
