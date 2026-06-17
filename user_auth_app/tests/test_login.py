from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from user_auth_app.models import User


class LoginApiTests(APITestCase):
    def setUp(self):
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

        data = {'username': 'testuser', 'password': 'geheim123'}

        response = self.client.post(self.url, data, format='json')

        if response.status_code != 200:
            print("Fehler im Serializer:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid_credentials(self):
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_data(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_response_format(self):
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
