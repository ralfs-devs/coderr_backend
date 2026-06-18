"""Integration test modules checking detailed data transitions, access guardrails, and validation workflows for individual user profiles."""

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileDetailApiTests(APITestCase):
    """Tests checking authentication rules, object mutation limits, and access validation for individual user profile endpoints.

    Attributes:
        user (User): Baseline account profile owner serving as the reference entity.
        url (str): Reversible routing locator mapped to a single distinct profile database identity.
    """

    def setUp(self):
        """Constructs a basic profile environment and registers dedicated user identities for resource routing lookups."""
        self.user = User.objects.create_user(
            username='test', email='t@t.de', password='pwd')
        self.url = reverse('profile-detail', kwargs={'pk': self.user.pk})

    def test_get_profile_detail(self):
        """Ensures that the resource owner can successfully read detailed properties of their specific profile endpoint."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'test')

    def test_patch_profile_detail(self):
        """Verifies that individual user profiles allow partial attribute mutations across single target fields."""
        self.client.force_authenticate(user=self.user)
        data = {'first_name': 'Max', 'email': 'newmail@exam.de'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Max')

    def test_patch_profile_by_other_user_forbidden(self):
        """Validates that foreign user requests cannot modify records outside their owned workspace limits."""
        other_user = User.objects.create_user(
            username='hacker',
            email='h@h.de',
            password='pwd'
        )
        self.client.force_authenticate(user=other_user)

        data = {'first_name': 'Hacked'}
        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_profile_unauthenticated_fails(self):
        """Blocks profile lookups from external network attempts lacking authorization headers."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_not_found(self):
        """Guarantees the system issues standard missing resource exceptions when accessing non-existent record identifiers."""
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_profile_invalid_email(self):
        """Confirms data integrity constraints drop profile updates presenting bad string structures in email fields."""
        self.client.force_authenticate(user=self.user)
        data = {'email': 'not_valid'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
