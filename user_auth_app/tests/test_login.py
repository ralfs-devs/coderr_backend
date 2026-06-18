"""Integration tests verifying payload processing paths and token delivery for the identity login interface."""

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from user_auth_app.models import User


class LoginApiTests(APITestCase):
    """Functional verification test collection checking connection authorization layers and token returns.

    Attributes:
        url (str): Reversible system workspace path targeting the auth endpoint.
        user (User): Reference database entry representing active authorization records.
        valid_payload (dict): Standard dictionary mapping validated reference login attributes.
    """

    def setUp(self):
        """Initializes testing contexts by creating identity references and resolving network paths."""
        self.url = reverse('user_login')
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='geheim123'
        )

        self.valid_payload = {
            "username": "testuser",
            "password": "geheim123"
        }

    def test_login_success(self):
        """Verifies validated plain matching credential strings pass security controls with success status codes."""
        data = {'username': 'testuser', 'password': 'geheim123'}

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid_credentials(self):
        """Ensures bad parameter pairings fail security challenges and report faulty request parameters."""
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_data(self):
        """Checks blank transaction models terminate early, flagging client communication faults."""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_response_format(self):
        """Confirms successful access validation packets return correct payload schemas and property fields."""
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', data)
        self.assertIn('username', data)
        self.assertIn('user_id', data)
        self.assertIn('email', data)
        self.assertEqual(data['username'], self.valid_payload['username'])
        self.assertEqual(data['email'], self.user.email)
