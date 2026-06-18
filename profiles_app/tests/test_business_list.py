"""Integration test modules checking data access restrictions and response actions for business profiles."""

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class BusinessListApiTests(APITestCase):
    """Tests checking data access restrictions and validation rules for listing business profiles.

    Attributes:
        user (User): A baseline authenticated test user entity.
        url (str): Target routing configuration address for business profile collections.
    """

    def setUp(self):
        """Prepares account records and target routing configuration addresses."""
        self.user = User.objects.create_user(
            username='biz1', password='pw', email='b1@b.com')
        self.url = reverse('business-profiles')

    def test_get_business_list_status_code(self):
        """Ensures an authenticated user can successfully fetch the business profiles collection."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_business_list_unauthenticated(self):
        """Guards endpoints against access attempts by unauthenticated network connections."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
