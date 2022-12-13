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
