from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from purly.user.models import User

from .models import Project

factory = APIRequestFactory()


class ProjectTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="test")  # noqa: S106

        self.client.defaults["HTTP_USER_AGENT"] = "test"
        self.client.force_login(user=self.user)

        self.url = "/api/v1/projects/"

    def test_create_project_full_payload(self):
        data = {
            "name": "test",
            "project_code": "test",
            "description": "test",
            "start_date": "2025-01-01",
            "end_date": "2025-01-07",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_project_partial_payload(self):
        data = {
            "name": "test",
            "description": "test",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_project_missing_required_fields(self):
        data = {
            "name": "test",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_project_name(self):
        Project.objects.create(
            name="test",
            project_code="test",
            description="test",
            start_date="2025-01-01",
            end_date="2025-01-07",
            created_by=self.user,
            updated_by=self.user,
        )

        data = {
            "name": "test",
            "project_code": "test",
            "description": "test",
            "start_date": "2025-01-01",
            "end_date": "2025-01-07",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_project_name_max_length(self):
        data = {"name": "test" * 256, "description": "test"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_name_is_invalid(self):
        data = {"name": "", "description": "test"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_user_cannot_create_project(self):
        self.client.logout()

        data = {"name": "test", "description": "test"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
