import pytest
from fastapi.testclient import TestClient

from src import app as app_module


ACTIVITY_NAME = "Chess Club"
ACTIVITY_PATH = "Chess%20Club"
EXISTING_EMAIL = "existing@example.com"


@pytest.fixture
def client(monkeypatch):
    activities = {
        ACTIVITY_NAME: {
            "description": "Test activity",
            "schedule": "Mondays at 3:00 PM",
            "max_participants": 10,
            "participants": [EXISTING_EMAIL],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_current_activities(client):
    # Arrange
    expected = {
        ACTIVITY_NAME: {
            "description": "Test activity",
            "schedule": "Mondays at 3:00 PM",
            "max_participants": 10,
            "participants": [EXISTING_EMAIL],
        }
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_signup_adds_participant(client):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_PATH}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {ACTIVITY_NAME}"}
    assert client.get("/activities").json()[ACTIVITY_NAME]["participants"] == [
        EXISTING_EMAIL,
        email,
    ]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_PATH}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert client.get("/activities").json()[ACTIVITY_NAME]["participants"] == [
        EXISTING_EMAIL
    ]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_path = "Unknown%20Activity"

    # Act
    response = client.post(
        f"/activities/{activity_path}/signup",
        params={"email": "new@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_signup_removes_participant(client):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_PATH}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {ACTIVITY_NAME}"}
    assert client.get("/activities").json()[ACTIVITY_NAME]["participants"] == []


def test_remove_signup_returns_not_found_for_missing_participant(client):
    # Arrange
    email = "missing@example.com"

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_PATH}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert client.get("/activities").json()[ACTIVITY_NAME]["participants"] == [
        EXISTING_EMAIL
    ]


def test_remove_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_path = "Unknown%20Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_path}/signup",
        params={"email": EXISTING_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}