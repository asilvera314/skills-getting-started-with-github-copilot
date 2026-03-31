"""Tests for Mergington High School Activities API using AAA pattern"""


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_success(self, client):
        """Test that GET /activities returns all activities successfully"""
        # Arrange
        expected_activity_names = {"Chess Club", "Programming Class", "Gym Class"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == expected_activity_names

    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have the correct structure"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in data.items():
            assert set(activity_data.keys()) == required_fields

    def test_get_activities_shows_participants(self, client):
        """Test that activities show existing participants"""
        # Arrange
        expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert data["Chess Club"]["participants"] == expected_chess_participants


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_succeeds(self, client):
        """Test that a new participant can successfully sign up"""
        # Arrange
        activity_name = "Chess Club"
        test_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        assert test_email in activities_response.json()[activity_name]["participants"]

    def test_signup_multiple_participants_increases_count(self, client):
        """Test that multiple participants can sign up and count increases"""
        # Arrange
        activity_name = "Programming Class"
        initial_count = len(client.get("/activities").json()[activity_name]["participants"])
        new_emails = ["alice@mergington.edu", "bob@mergington.edu"]

        # Act
        for email in new_emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200

        # Assert
        final_data = client.get("/activities").json()[activity_name]
        assert len(final_data["participants"]) == initial_count + 2
        assert all(email in final_data["participants"] for email in new_emails)

    def test_signup_duplicate_participant_fails(self, client):
        """Test that duplicate signup returns 400 error"""
        # Arrange
        activity_name = "Chess Club"
        duplicate_email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={duplicate_email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signup for non-existent activity returns 404"""
        # Arrange
        fake_activity = "Fake Activity"
        test_email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_succeeds(self, client):
        """Test that an existing participant can be unregistered"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        initial_count = len(client.get("/activities").json()[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email_to_remove}"
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        final_data = client.get("/activities").json()[activity_name]
        assert len(final_data["participants"]) == initial_count - 1
        assert email_to_remove not in final_data["participants"]

    def test_unregister_allows_reregistration(self, client):
        """Test that a participant can re-register after being unregistered"""
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"

        # Act - Remove participant
        remove_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert remove_response.status_code == 200

        # Act - Re-register same participant
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert signup_response.status_code == 200
        assert email in client.get("/activities").json()[activity_name]["participants"]

    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregistering non-existent participant returns 400"""
        # Arrange
        activity_name = "Programming Class"
        fake_email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={fake_email}"
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from non-existent activity returns 404"""
        # Arrange
        fake_activity = "Fake Activity"
        test_email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{fake_activity}/unregister?email={test_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
