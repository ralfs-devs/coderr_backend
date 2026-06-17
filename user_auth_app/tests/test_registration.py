
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class RegistrationApiTests(APITestCase):
    def setUp(self):
        self.url = reverse('user_registration')
        self.valid_payload = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }

    def test_registration_success(self):
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)

    def test_registration_password_mismatch(self):
        payload = self.valid_payload.copy()
        payload['repeated_password'] = 'differentPassword'
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_data(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_response_format(self):
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', data)
        self.assertIn('username', data)
        self.assertIn('user_id', data)
        self.assertIn('email', data)
        self.assertEqual(data['username'], self.valid_payload['username'])
        self.assertEqual(data['email'], self.valid_payload['email'])

    def test_registration_email_mismatch(self):
        payload = self.valid_payload.copy()
        payload['password'] = 'password123'
        payload['repeated_password'] = 'wrongword456'
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_empty_password(self):
        payload = self.valid_payload.copy()
        payload['password'] = ''
        payload['repeated_password'] = ''
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_registration_empty_email(self):
        payload = self.valid_payload.copy()
        payload['email'] = ''
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_empty_username(self):
        payload = self.valid_payload.copy()
        payload['username'] = ''
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_registration_duplicate_username(self):

        response1 = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response2.data)

    def test_registration_duplicate_email(self):

        response1 = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        payload = self.valid_payload.copy()
        payload['username'] = 'differentUsername'
        response2 = self.client.post(
            self.url, payload, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response2.data)

    def test_registration_invalid_email_format(self):
        payload = self.valid_payload.copy()
        payload['email'] = 'invalid-email-format'
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
