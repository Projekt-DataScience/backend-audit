from main import client


def test_get_lpa_questions():
    response = client.get("/api/audit/lpa_question/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    if len(response.json()) > 0:
        first = response.json()[0]
        assert first.get("id") is not None
        assert first.get("question") is not None
        assert isinstance(first.get("question"), str)
        assert first.get("description") is not None
        assert isinstance(first.get("description"), str)
        assert isinstance(first.get("category"), dict)
        assert isinstance(first.get("layer"), dict)
        assert isinstance(first.get("group"), dict)


def test_get_lpa_question_by_id():
    response = client.get("/api/audit/lpa_question/1")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json().get("id") == 1
    assert response.json().get("question") is not None
    assert isinstance(response.json().get("question"), str)
    assert response.json().get("description") is not None
    assert isinstance(response.json().get("description"), str)
    assert isinstance(response.json().get("category"), dict)
    assert isinstance(response.json().get("layer"), dict)
    assert isinstance(response.json().get("group"), dict)


def test_lpa_question_by_id_not_found():
    response = client.get("/api/audit/lpa_question/999999999")

    assert response.status_code == 404


def test_get_lpa_questions_of_audit():
    response_audit = client.get("/api/audit/lpa_audit/1")

    if response_audit.status_code == 404:
        print("Audit not found, aborting test test_get_lpa_questions_of_audit")
    else:
        response = client.get("/api/audit/lpa_question/audit/1")

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == len(
            response_audit.json().get("questions"))


def test_create_and_delete_lpa_question():
    data = {
        "question": "test question",
        "description": "test question",
        "category_id": 1,
        "layer_id": 1,
        "group_id": 1
    }

    response = client.post("/api/audit/lpa_question", json=data)

    assert response.status_code == 200
    question = response.json()
    assert isinstance(question, dict)
    assert question.get("id") is not None
    assert question.get("question") == "test question"
    assert question.get("description") == "test question"
    assert question.get("category").get("id") == 1
    assert question.get("layer").get("id") == 1
    assert question.get("group").get("id") == 1

    id = response.json().get("id")
    response = client.get("/api/audit/lpa_question/" + str(id))

    question = response.json()
    assert response.status_code == 200
    assert question.get("question") == "test question"
    assert question.get("description") == "test question"
    assert question.get("category").get("id") == 1
    assert question.get("layer").get("id") == 1
    assert question.get("group").get("id") == 1

    response = client.post("/api/audit/lpa_question/", json=data)
    assert response.status_code == 200

    response = client.post("/api/audit/lpa_question/delete/" + str(id))
    assert response.status_code == 200

    response = client.get("/api/audit/lpa_question/" + str(id))
    assert response.status_code == 404