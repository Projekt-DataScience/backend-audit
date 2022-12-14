import os
import requests
import string
import random

from datetime import datetime

from backend_db_lib.manager import DatabaseManager
from backend_db_lib.models import base

env = {}
with open(".env", "r") as f:
    lines = f.read().splitlines()
    for line in lines:
        print(line)
        if "=" in line:
            key, value = line.split("=")
            env[key] = value.strip()

print(env)

DATABASE_URL = f"postgresql://{env['DB_USER']}:{env['DB_PASSWORD']}@127.0.0.1:{env['DB_PORT']}/{env['DB_NAME']}"

test_database = os.environ.get("TEST_DATABASE")
if test_database:
    DATABASE_URL = test_database


def create_db():
    db = DatabaseManager(base, DATABASE_URL)
    db.drop_all()
    db.create_all()
    db.create_initial_data()


URL = "http://localhost:8000/api/audit"


def create_answer_reasons(n=3):
    ENDPOINT = "/lpa_answer/reason"

    ids = []
    for i in range(n):
        response = requests.post(
            URL + ENDPOINT,
            json={"description": "".join(random.choices(
                string.ascii_uppercase + string.digits, k=10))}
        )

        ids.append(response.json()["id"])

    return ids


def create_audit(question_ids, n=5):
    ENDPOINT = "/lpa_audit"

    now = datetime.now()
    DATA = {
        "due_date": f"{now.year+1}-12-22T00:00:00",
        "auditor": 1,
        "assigned_group": 1,
        "assigned_layer": 1,
        "question_count": random.randint(2, len(question_ids)),
    }

    ids = []
    for i in range(n):
        response = requests.post(
            URL + ENDPOINT,
            json=DATA
        )

        # print(response.json())
        ids.append(response.json()["id"])

    return ids


if __name__ == "__main__":
    print("Creating database...")
    create_db()
    print("Database created.")

    print("Creating audits...")
    audit_ids = create_audit(question_ids)
    print(audit_ids)
