from main import client
from helpers.auth import login


def test_get_analytics_by_group():
    # Login
    access_token = login()

    # Get analytics of group
    response = client.get("/api/audit/analytics/groups", headers={"Authorization": f"Bearer {access_token}"})

    # Tests
    assert response.status_code == 200


def test_get_audit_analytics():
    # Login
    access_token = login()

    # Get analytics of group
    response = client.get("/api/audit/analytics/audits", headers={"Authorization": f"Bearer {access_token}"})

    # Tests
    assert response.status_code == 200

def test_get_audit_analytics_by_user_id():
    # Login
    access_token = login()

    # Get analytics of group
    response = client.get("/api/audit/analytics/audits/1", headers={"Authorization": f"Bearer {access_token}"})

    # Tests
    assert response.status_code == 200
