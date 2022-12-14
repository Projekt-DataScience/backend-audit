from main import client


def test_get_status():
    response = client.get("/api/audit/")
    assert response.status_code == 200
    assert response.json().get("Status") == "Up"

    response = client.get("/api/audit/healthcheck")
    assert response.status_code == 200
    assert response.json().get("Status") == "Up"
