from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from purly.user.models import User

factory = APIRequestFactory()


class ProjectTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="test")  # noqa: S106
        self.client.force_login(user=self.user)

    def test_create_project(self):
        url = "/api/v1/projects/"
        data = {
            "name": "test",
            "project_code": "test",
            "description": "test",
            "start_date": "2025-01-01",
            "end_date": "2025-01-01",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_partial_project(self):
        url = "/api/v1/projects/"
        data = {
            "name": "test",
            "description": "test",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_missing_field_project(self):
        url = "/api/v1/projects/"
        data = {
            "name": "test",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
