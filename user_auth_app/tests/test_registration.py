
"""Integration tests verifying payload constraint validation and token generation pipelines for the registration endpoint."""

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class RegistrationApiTests(APITestCase):
    """Functional test collection covering identity provisioning, constraint validation, and field redundancy limits.

    Attributes:
        url (str): Reversible module path pointing to the account creation endpoint.
        valid_payload (dict): Baseline collection hosting structured mock user initialization variables.
    """

    def setUp(self):
        """Initializes testing contexts by targeting endpoints and preparing raw submission values."""
        self.url = reverse('user_registration')
        self.valid_payload = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }

    def test_registration_success(self):
        """Validates that complete, compliant registration packets trigger persistence actions and assign authorization signatures."""
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)

    def test_registration_password_mismatch(self):
        """Confirms that asymmetrical credentials block persistence execution and fail parsing validation loops."""
        payload = self.valid_payload.copy()
        payload['repeated_password'] = 'differentPassword'
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_data(self):
        """Confirms that processing vacant submission dictionaries blocks framework entry and raises standard validation exceptions."""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_type(self):
        """Confirms that registering a standard user without providing a type field triggers a validation error."""
        payload = self.valid_payload.copy()
        payload.pop('type')
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type', response.data)

    def test_registration_invalid_type(self):
        """Validates that submitting an unsupported operational profile type gets rejected by validation rules."""
        payload = self.valid_payload.copy()
        payload['type'] = 'admin'
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type', response.data)

    def test_registration_response_format(self):
        """Ensures creation responses return structured accounts mirroring initialized fields along with an explicit key identifier."""
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
        """Validates error response traps when secondary structural confirmation arguments deviate from original inputs."""
        payload = self.valid_payload.copy()
        payload['password'] = 'password123'
        payload['repeated_password'] = 'wrongword456'
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_empty_password(self):
        """Verifies zero-length credential properties fail core serialization rules and return field-specific flags."""
        payload = self.valid_payload.copy()
        payload['password'] = ''
        payload['repeated_password'] = ''
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_registration_empty_email(self):
        """Ensures submission arrays featuring blank email values terminate processing routines, exposing validation logs."""
        payload = self.valid_payload.copy()
        payload['email'] = ''
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_empty_username(self):
        """Ensures empty system handle attributes fail data entry requirements and register error dictionaries."""
        payload = self.valid_payload.copy()
        payload['username'] = ''
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_registration_duplicate_username(self):
        """Confirms database unique constraints block duplicate profile requests using identical system handles."""
        response1 = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response2.data)

    def test_registration_duplicate_email(self):
        """Confirms unique schema settings prevent concurrent records sharing matching mailbox strings."""
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
        """Ensures that structural syntax validation catches mail tokens that deviate from standard mailbox patterns."""
        payload = self.valid_payload.copy()
        payload['email'] = 'invalid-email-format'
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
