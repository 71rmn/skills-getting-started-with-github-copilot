import unittest

from fastapi.testclient import TestClient

from src.app import activities, app


class UnregisterParticipantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.activity_name = "Test Activity"
        self.email = "student@mergington.edu"
        self.previous_activity = activities.get(self.activity_name)
        activities[self.activity_name] = {"participants": [self.email]}

    def tearDown(self):
        if self.previous_activity is None:
            activities.pop(self.activity_name, None)
        else:
            activities[self.activity_name] = self.previous_activity

    def test_unregister_participant(self):
        response = self.client.delete(
            f"/activities/{self.activity_name}/participants",
            params={"email": self.email},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": f"Unregistered {self.email} from {self.activity_name}"},
        )
        self.assertEqual(activities[self.activity_name]["participants"], [])

    def test_unregister_rejects_unknown_activity_or_participant(self):
        unknown_activity = self.client.delete(
            "/activities/Unknown/participants",
            params={"email": self.email},
        )
        unknown_participant = self.client.delete(
            "/activities/Chess Club/participants",
            params={"email": "not-signed-up@mergington.edu"},
        )

        self.assertEqual(unknown_activity.status_code, 404)
        self.assertEqual(unknown_participant.status_code, 404)


if __name__ == "__main__":
    unittest.main()
