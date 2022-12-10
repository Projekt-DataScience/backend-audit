import requests
import string
import random

from datetime import datetime

URL = "http://localhost:8000"

def create_question_categories():
    ENDPOINT = "/lpa_question_category/question_category"
    CATEGORIES = ["Arbeitsschutz", "Qualitätssicherung"]

    ids = []
    for category in CATEGORIES:
        response = requests.post(
            URL + ENDPOINT,
            json={"category_name": category}
        )

        ids.append(response.json()["id"])

    return ids


def create_questions(category_ids, n=10):
    ENDPOINT = "/lpa_question"
    DATA = {
        "question": "string",
        "description": "string",
        "category_id": category_ids[0],
        "layer_id": 1,
        "group_id": 1
    }

    ids = []
    for i in range(n):
        DATA["question"] = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
        DATA["description"] = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

        response = requests.post(
            URL + ENDPOINT,
            json=DATA
        )

        ids.append(response.json()["id"])

    return ids

def create_answer_reasons(n=3):
    ENDPOINT = "/lpa_answer/reason"
    
    ids = []
    for i in range(n):
        response = requests.post(
            URL + ENDPOINT,
            json={"description": "".join(random.choices(string.ascii_uppercase + string.digits, k=10))}
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

        #print(response.json())
        ids.append(response.json()["id"])

    return ids


if __name__ == "__main__":
    print("Creating question categories...")
    category_ids = create_question_categories()
    print(category_ids)

    print("Creating questions...")
    question_ids = create_questions(category_ids)
    print(question_ids)

    print("Creating answer reasons...")
    reason_ids = create_answer_reasons()
    print(reason_ids)

    print("Creating audits...")
    audit_ids = create_audit(question_ids)
    print(audit_ids)