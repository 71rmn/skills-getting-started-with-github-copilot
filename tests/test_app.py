import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


ACTIVITY_NAME = "Test Activity"
PARTICIPANT_EMAIL = "student@mergington.edu"


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def activity(monkeypatch):
    monkeypatch.setitem(
        activities,
        ACTIVITY_NAME,
        {
            "description": "A test activity",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": [PARTICIPANT_EMAIL],
        },
    )
    return ACTIVITY_NAME


def test_signup_participant(client, activity):
    # Arrange
    email = "new-student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_rejects_duplicate_participant(client, activity):
    # Arrange
    email = PARTICIPANT_EMAIL

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": PARTICIPANT_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_participant(client, activity):
    # Arrange
    email = PARTICIPANT_EMAIL

    # Act
    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity}"
    }
    assert email not in activities[activity]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": PARTICIPANT_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_unknown_participant(client, activity):
    # Arrange
    email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
