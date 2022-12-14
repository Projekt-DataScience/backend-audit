from main import client
from helpers.auth import login


def test_get_answer_reasons():
    token = login()
    response = client.get("/api/audit/lpa_answer/reason", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    if len(response.json()) > 0:
        assert response.json()[0].get("id") is not None
        assert response.json()[0].get("description") is not None


def test_create_and_delete_answer_reason():
    token = login()
    data = {
        "description": "my reason"
    }

    response = client.post("/api/audit/lpa_answer/reason", json=data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("id") is not None
    assert response.json().get("description") == "my reason"

    id = response.json().get("id")
    response = client.post("/api/audit/lpa_answer/reason/delete/" + str(id), headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_create_update_and_delete_answer_reason():
    token = login()
    data = {
        "description": "my reason"
    }

    response = client.post("/api/audit/lpa_answer/reason", json=data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("id") is not None
    assert response.json().get("description") == "my reason"

    id = response.json().get("id")

    data = {
        "description": "my reason update"
    }
    response = client.post(
        "/api/audit/lpa_answer/reason/" + str(id), json=data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("id") == id
    assert response.json().get("description") == "my reason update"

    response = client.post("/api/audit/lpa_answer/reason/delete/" + str(id), headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
