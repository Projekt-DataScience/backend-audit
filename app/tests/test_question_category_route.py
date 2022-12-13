from main import client


def test_get_question_categories():
    response = client.get("/api/audit/lpa_question_category/question_category")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    if len(response.json()) > 0:
        assert response.json()[0].get("id") is not None
        assert response.json()[0].get("category_name") is not None


def test_get_question_category_by_id():
    response = client.get(
        "/api/audit/lpa_question_category/question_category/1")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("id") == 1
    assert response.json().get("category_name") is not None


def test_get_question_category_by_id_not_found():
    response = client.get(
        "/api/audit/lpa_question_category/question_category/999999999")
    assert response.status_code == 404


def test_update_question_category():
    response = client.get(
        "/api/audit/lpa_question_category/question_category/1")
    org_category_name = response.json().get("category_name")

    new_category_name = "New Category Name"
    response = client.post("/api/audit/lpa_question_category/question_category/1",
                           json={"category_name": new_category_name})

    assert response.status_code == 200
    assert response.json().get("id") == 1
    assert response.json().get("category_name") == new_category_name

    response = client.post("/api/audit/lpa_question_category/question_category/1",
                           json={"category_name": org_category_name})


def test_create_and_delete_category():
    data = {
        "category_name": "New Category"
    }
    response = client.post(
        "/api/audit/lpa_question_category/question_category", json=data)

    assert response.status_code == 200

    response = response.json()
    assert isinstance(response, dict)
    assert response.get("id") is not None
    assert response.get("category_name") == "New Category"

    id = response.get("id")
    response = client.post(
        f"/api/audit/lpa_question_category/question_category/delete/{id}")
    assert response.status_code == 200

    response = client.get(
        f"/api/audit/lpa_question_category/question_category/{id}")
    assert response.status_code == 404
