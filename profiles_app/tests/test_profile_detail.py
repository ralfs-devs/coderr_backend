from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileDetailApiTests(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username='test', email='t@t.de', password='pwd')
        self.url = reverse('profile-detail', kwargs={'pk': self.user.pk})

    def test_get_profile_detail(self):

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'test')

    def test_patch_profile_detail(self):

        self.client.force_authenticate(user=self.user)
        data = {'first_name': 'Max', 'email': 'newmail@exam.de'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Max')

    def test_patch_profile_by_other_user_forbidden(self):

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

        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_not_found(self):

        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_profile_invalid_email(self):

        self.client.force_authenticate(user=self.user)
        data = {'email': 'not_valid'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
