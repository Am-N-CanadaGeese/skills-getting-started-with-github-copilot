"""
Tests for the High School Management System API

This test module contains comprehensive tests for all endpoints of the FastAPI
application using the AAA (Arrange-Act-Assert) testing pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


# ============================================================================
# GET /activities - Retrieve all activities
# ============================================================================

def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities"""
    # Arrange
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Soccer Club",
        "Art Club",
        "Drama Club",
        "Debate Club",
        "Science Club"
    ]
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities_data = response.json()
    assert len(activities_data) == 9
    for activity_name in expected_activities:
        assert activity_name in activities_data


def test_get_activities_returns_activity_details(client):
    """Test that GET /activities returns complete activity details"""
    # Arrange
    # Act
    response = client.get("/activities")
    activities_data = response.json()
    
    # Assert
    assert response.status_code == 200
    chess_club = activities_data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


# ============================================================================
# GET / - Root redirect
# ============================================================================

def test_root_redirects_to_static_index(client):
    """Test that GET / redirects to /static/index.html"""
    # Arrange
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


# ============================================================================
# POST /activities/{activity_name}/signup - Sign up for an activity
# ============================================================================

def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_signup_for_activity_already_signed_up(client):
    """Test that signing up twice returns 400 error"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already a participant
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_for_nonexistent_activity(client):
    """Test that signing up for nonexistent activity returns 404 error"""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_signup_verification_participant_added(client):
    """Test that signup actually adds the participant to the activity"""
    # Arrange
    activity_name = "Programming Class"
    email = "verify@mergington.edu"
    
    # Act - Sign up
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Act - Get activities to verify
    get_response = client.get("/activities")
    activities_data = get_response.json()
    
    # Assert
    assert signup_response.status_code == 200
    assert email in activities_data[activity_name]["participants"]


# ============================================================================
# DELETE /activities/{activity_name}/participants - Remove from activity
# ============================================================================

def test_remove_participant_success(client):
    """Test successful removal of a participant from an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Existing participant
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_remove_nonexistent_participant(client):
    """Test that removing nonexistent participant returns 404 error"""
    # Arrange
    activity_name = "Chess Club"
    email = "notaparticipant@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_remove_participant_from_nonexistent_activity(client):
    """Test that removing participant from nonexistent activity returns 404 error"""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_remove_verification_participant_removed(client):
    """Test that removal actually removes the participant from the activity"""
    # Arrange
    activity_name = "Drama Club"
    email = "mason@mergington.edu"  # Existing participant
    
    # Act - Remove participant
    remove_response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    
    # Act - Get activities to verify
    get_response = client.get("/activities")
    activities_data = get_response.json()
    
    # Assert
    assert remove_response.status_code == 200
    assert email not in activities_data[activity_name]["participants"]
