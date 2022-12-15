from main import client
from helpers.auth import login

def test_get_question_categories():
    token = login(client)

    response = client.get("/api/audit/lpa_question_category/question_category", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    if len(response.json()) > 0:
        assert response.json()[0].get("id") is not None
        assert response.json()[0].get("category_name") is not None


def test_get_question_category_by_id():
    token = login(client)

    response = client.get(
        "/api/audit/lpa_question_category/question_category/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("id") == 1
    assert response.json().get("category_name") is not None


def test_get_question_category_by_id_not_found():
    token = login(client)
    
    response = client.get(
        "/api/audit/lpa_question_category/question_category/999999999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_update_question_category():
    token = login(client)

    response = client.get(
        "/api/audit/lpa_question_category/question_category/1", headers={"Authorization": f"Bearer {token}"})
    org_category_name = response.json().get("category_name")

    new_category_name = "New Category Name"
    response = client.post("/api/audit/lpa_question_category/question_category/1",
                           json={"category_name": new_category_name}, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json().get("id") == 1
    assert response.json().get("category_name") == new_category_name

    response = client.post("/api/audit/lpa_question_category/question_category/1",
                           json={"category_name": org_category_name}, headers={"Authorization": f"Bearer {token}"})


def test_create_and_delete_category():
    token = login(client)
    
    data = {
        "category_name": "New Category"
    }
    response = client.post(
        "/api/audit/lpa_question_category/question_category", json=data, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200

    response = response.json()
    assert isinstance(response, dict)
    assert response.get("id") is not None
    assert response.get("category_name") == "New Category"

    id = response.get("id")
    response = client.post(
        f"/api/audit/lpa_question_category/question_category/delete/{id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    response = client.get(
        f"/api/audit/lpa_question_category/question_category/{id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
