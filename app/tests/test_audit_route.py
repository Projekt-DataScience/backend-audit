from datetime import datetime, timedelta
from main import client


def test_get_audits():
    response = client.get("/api/audit/lpa_audit")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_audit_by_id():
    response = client.get("/api/audit/lpa_audit/1")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("id") == 1


def test_get_audit_by_id_not_found():
    response = client.get("/api/audit/lpa_audit/999999999")
    assert response.status_code == 404


def test_complete_audits():
    response = client.get("/api/audit/lpa_audit/complete")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_and_delete_spontanous_audit():
    date = datetime.now() + timedelta(days=10)

    data = {
        "due_date": date.strftime("%Y-%m-%dT%H:%M:%S"),
        "auditor": 1,
        "assigned_group": 1,
        "assigned_layer": 1,
        "question_count": 3,
    }
    response = client.post("/api/audit/lpa_audit", json=data)

    assert response.status_code == 200

    response = response.json()
    assert isinstance(response, dict)
    assert response.get("id") is not None
    assert response.get("due_date") == date.strftime("%Y-%m-%dT%H:%M:%S")
    assert response.get("auditor") == 1
    assert response.get("assigned_group") == 1
    assert response.get("assigned_layer") == 1
    assert response.get("question_count") == 3
    assert response.get("audited_user_id") is None
    assert response.get("duration") is None
    assert len(response.get("questions")) == 3

    # Checking if questions are unique
    questions = response.get("questions")
    question_titles = set([question.get("question") for question in questions])
    assert len(question_titles) == 3

    id = response.get("id")

    response = client.post(f"/api/audit/lpa_audit/delete/{id}")
    assert response.status_code == 200

    # Checking if deleted
    response = client.get(f"/api/audit/lpa_audit/{id}")
    assert response.status_code == 404


def test_get_open_audits_of_user():
    date = datetime.now() + timedelta(days=10)

    data = {
        "due_date": date.strftime("%Y-%m-%dT%H:%M:%S"),
        "auditor": 1,
        "assigned_group": 1,
        "assigned_layer": 1,
        "question_count": 3,
    }
    response = client.post("/api/audit/lpa_audit", json=data)
    id = response.json().get("id")

    response = client.get("/api/audit/lpa_audit/open/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    response = client.post(f"/api/audit/lpa_audit/delete/{id}")


def test_get_open_audits_of_user_not_found():
    response = client.get("/api/audit/lpa_audit/open/999999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
