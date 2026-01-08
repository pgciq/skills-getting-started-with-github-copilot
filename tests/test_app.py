"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


def reset_activities():
    """Reset the activities data to initial state"""
    from src.app import activities

    # Reset to initial state
    activities.clear()
    activities.update({
        "Basketball": {
            "description": "Team basketball practice and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Soccer": {
            "description": "Competitive soccer team for all skill levels",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["jordan@mergington.edu", "casey@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and mixed media",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lily@mergington.edu"]
        }
    })


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index"""
        reset_activities()
        response = client.get("/")
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test the activities endpoints"""

    def test_get_activities(self, client):
        """Test getting all activities"""
        reset_activities()
        response = client.get("/activities")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball" in data
        assert "Soccer" in data
        assert "Art Club" in data

        # Check structure of Basketball activity
        basketball = data["Basketball"]
        assert "description" in basketball
        assert "schedule" in basketball
        assert "max_participants" in basketball
        assert "participants" in basketball
        assert basketball["max_participants"] == 15
        assert "alex@mergington.edu" in basketball["participants"]

    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        reset_activities()
        response = client.post("/activities/Basketball/signup?email=test@mergington.edu")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "Signed up test@mergington.edu for Basketball" == data["message"]

        # Verify the participant was added
        response = client.get("/activities")
        activities = response.json()
        assert "test@mergington.edu" in activities["Basketball"]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        reset_activities()
        response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "Activity not found" == data["detail"]

    def test_signup_already_signed_up(self, client):
        """Test signup when student is already signed up"""
        reset_activities()
        # First signup
        client.post("/activities/Basketball/signup?email=test@mergington.edu")

        # Try to signup again
        response = client.post("/activities/Basketball/signup?email=test@mergington.edu")
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "Student already signed up for this activity" == data["detail"]

    def test_remove_participant_successful(self, client):
        """Test successful removal of a participant"""
        reset_activities()
        # First verify the participant exists
        response = client.get("/activities")
        activities = response.json()
        assert "alex@mergington.edu" in activities["Basketball"]["participants"]

        # Remove the participant
        response = client.delete("/activities/Basketball/participants/alex@mergington.edu")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "Removed alex@mergington.edu from Basketball" == data["message"]

        # Verify the participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert "alex@mergington.edu" not in activities["Basketball"]["participants"]

    def test_remove_participant_activity_not_found(self, client):
        """Test removing participant from non-existent activity"""
        reset_activities()
        response = client.delete("/activities/NonExistent/participants/test@mergington.edu")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "Activity not found" == data["detail"]

    def test_remove_participant_not_signed_up(self, client):
        """Test removing participant who is not signed up"""
        reset_activities()
        response = client.delete("/activities/Basketball/participants/notsignedup@mergington.edu")
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "Student is not signed up for this activity" == data["detail"]