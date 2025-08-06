from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from purly.user.models import User

factory = APIRequestFactory()


class AddressTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="test")  # noqa: S106

        self.client.defaults["HTTP_USER_AGENT"] = "test"
        self.client.force_login(user=self.user)

        self.url = "/api/v1/addresses/"

    def test_create_address_full_payload(self):
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
            "delivery_instructions": "test,",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_partial_payload(self):
        data = {
            "name": "test",
            "attention": "test",
            "street1": "test",
            "city": "test",
            "state": "test",
            "zip_code": "test",
            "country": "test",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_missing_required_fields(self):
        data = {
            "name": "test",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_address_name_max_length(self):
        data = {
            "name": "test" * 256,
            "attention": "test",
            "street1": "test",
            "city": "test",
            "state": "test",
            "zip_code": "test",
            "country": "test",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_name_is_invalid(self):
        data = {
            "name": "",
            "attention": "test",
            "street1": "test",
            "city": "test",
            "state": "test",
            "zip_code": "test",
            "country": "test",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_user_cannot_create_project(self):
        self.client.logout()

        data = {
            "name": "",
            "attention": "test",
            "street1": "test",
            "city": "test",
            "state": "test",
            "zip_code": "test",
            "country": "test",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
