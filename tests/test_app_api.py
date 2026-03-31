import uuid
from urllib.parse import quote


def test_get_activities_status_code_200(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_success(client):
    # Arrange
    email = f"test-{uuid.uuid4().hex}@mergington.edu"
    activity_name = "Chess Club"
    endpoint = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    response = client.post(endpoint)

    # Assert
    assert response.status_code == 200
    assert email in response.json().get("message", "")

    # Verify participant has been added
    activities_resp = client.get("/activities")
    assert activities_resp.status_code == 200
    assert email in activities_resp.json()[activity_name]["participants"]


def test_signup_duplicate_participant_error(client):
    # Arrange
    email = f"test-{uuid.uuid4().hex}@mergington.edu"
    activity_name = "Chess Club"
    endpoint = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act - first signup
    first_response = client.post(endpoint)
    # Arrange implicit: now user is signed up
    assert first_response.status_code == 200

    # Act - duplicate signup
    second_response = client.post(endpoint)

    # Assert
    assert second_response.status_code == 400
    assert second_response.json().get("detail") == "Student already signed up"


def test_remove_participant_success(client):
    # Arrange
    email = f"test-{uuid.uuid4().hex}@mergington.edu"
    activity_name = "Chess Club"
    signup_endpoint = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    remove_endpoint = f"/activities/{quote(activity_name)}/participants?email={quote(email)}"

    signup_resp = client.post(signup_endpoint)
    assert signup_resp.status_code == 200

    # Act
    delete_resp = client.delete(remove_endpoint)

    # Assert
    assert delete_resp.status_code == 200
    assert "Removed" in delete_resp.json().get("message", "")

    # Verify participant removed
    activities_resp = client.get("/activities")
    assert activities_resp.status_code == 200
    assert email not in activities_resp.json()[activity_name]["participants"]


def test_remove_nonexistent_activity_404(client):
    # Arrange
    email = "nobody@mergington.edu"
    activity_name = "Nonexistent Activity"
    endpoint = f"/activities/{quote(activity_name)}/participants?email={quote(email)}"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 404
