from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic checks
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure the test email is not already present
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    participants = activities[activity]["participants"]
    if email in participants:
        # Remove if already present so the test can run idempotently
        client.delete(f"/activities/{activity}/participants?email={email}")

    # Sign up
    signup_resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_resp.status_code == 200
    assert "Signed up" in signup_resp.json().get("message", "")

    # Verify participant was added
    resp = client.get("/activities")
    activities = resp.json()
    assert email in activities[activity]["participants"]

    # Now unregister
    del_resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert del_resp.status_code == 200
    assert "Unregistered" in del_resp.json().get("message", "")

    # Verify participant removed
    resp = client.get("/activities")
    activities = resp.json()
    assert email not in activities[activity]["participants"]
