import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


def test_unregister_removes_participant(client):
    activity_name = "Chess Club"
    email = "test-unregister@mergington.edu"
    participants = activities[activity_name]["participants"]
    participants.append(email)

    try:
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in participants
    finally:
        if email in participants:
            participants.remove(email)


def test_unregister_returns_404_for_unregistered_participant(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "not-signed-up@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_activities_response_is_not_cached(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"


def test_activities_include_successful_signup(client):
    activity_name = "Basketball Team"
    email = "test-signup-refresh@mergington.edu"
    participants = activities[activity_name]["participants"]

    try:
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )
        activities_response = client.get("/activities")

        assert signup_response.status_code == 200
        assert email in activities_response.json()[activity_name]["participants"]
    finally:
        if email in participants:
            participants.remove(email)
