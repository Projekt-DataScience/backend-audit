from main import client

from db import RECURRENCE_TYPES
from helpers.auth import login


def test_get_rhytms():
    token = login()
    response = client.get("/api/audit/planned", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_create_and_get_by_id_rhytm():
    token = login()
    data = {
        "id": 0,
        "auditor_id": 1,
        "group_id": 1,
        "layer_id": 1,
        "question_count": 2,
        "recurrence_type": "weekly",
        "values": [
            "monday"
        ]
    }

    response = client.post("/api/audit/planned", json=data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json().get("id") is not None
    assert response.json().get("auditor_id") == 1
    assert response.json().get("group_id") == 1
    assert response.json().get("layer_id") == 1
    assert response.json().get("question_count") == 2
    assert response.json().get("recurrence_type") == "weekly"
    assert response.json().get("values") == ["monday"]

    id = response.json().get("id")
    response = client.get(f"/api/audit/planned/{id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json().get("id") == id
    assert response.json().get("auditor_id") == 1
    assert response.json().get("group_id") == 1
    assert response.json().get("layer_id") == 1
    assert response.json().get("question_count") == 2
    assert response.json().get("type") == "weekly"
    assert response.json().get("values") == ["monday"]


def test_get_recurrence_types():
    token = login()
    response = client.get("/api/audit/planned/types", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == len(RECURRENCE_TYPES.TYPES)
    assert response.json() == RECURRENCE_TYPES.TYPES


def test_recurrence_values():
    token = login()
    for type in RECURRENCE_TYPES.TYPES:
        response = client.get(f"/api/audit/planned/values/{type}", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == len(RECURRENCE_TYPES.VALUES[type])
        assert response.json() == RECURRENCE_TYPES.VALUES[type]
