from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class BusinessListApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='biz1', password='pw', email='b1@b.com')
        self.url = reverse('business-profiles')

    def test_get_business_list_status_code(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_business_list_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
