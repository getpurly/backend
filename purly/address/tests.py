from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from purly.user.models import User

factory = APIRequestFactory()


class AddressTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="test")  # noqa: S106
        self.client.force_login(user=self.user)

    def test_create_address(self):
        url = "/api/v1/addresses/"
        data = {
            "name": "test",
            "address_code": "test",
            "description": "test",
            "attention": "test",
            "phone": "test",
            "street1": "test",
            "street2": "test",
            "city": "test",
            "state": "test",
            "zip_code": "test",
            "country": "test",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_partial_address(self):
        url = "/api/v1/addresses/"
        data = {
            "name": "test",
            "attention": "test",
            "street1": "test",
            "city": "test",
            "state": "test",
            "zip_code": "test",
            "country": "test",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_missing_field_address(self):
        url = "/api/v1/addresses/"
        data = {
            "name": "test",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
