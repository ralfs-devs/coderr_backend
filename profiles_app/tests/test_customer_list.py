from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from ..models import Profile

User = get_user_model()


class CustomerListApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='customer1', password='pw', email='c1@c.com')
        self.url = reverse('customer-profiles')

    def test_get_customer_list_success(self):

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 0)

    def test_get_customer_list_unauthenticated(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_customer_list_field_name(self):

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('uploaded_at', response.data[0])
        self.assertNotIn('created_at', response.data[0])

    def test_only_customer_profiles_in_list(self):

        other_user = User.objects.create_user(
            username='biz1', password='pw', email='b1@b.com'
        )
        other_user.type = 'business'
        other_user.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'customer')
        self.assertEqual(response.data[0]['username'], 'customer1')


class CustomerListApiTests(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username='tester', password='pw', email='tester@test.com'
        )
        self.user.type = 'customer'
        self.user.save()

        self.url = reverse('customer-profiles')

    def test_customer_list_structure_and_filtering(self):

        biz_user = User.objects.create_user(
            username='biz1', password='pw', email='biz1@test.com'
        )
        biz_user.type = 'business'
        biz_user.save()

        biz_profile = Profile.objects.get(user=biz_user)
        biz_profile.first_name = 'Biz'
        biz_profile.save()

        c1 = User.objects.create_user(
            username='jane', password='pw', email='jane@test.com'
        )
        c1.type = 'customer'
        c1.save()

        c1_profile = Profile.objects.get(user=c1)
        c1_profile.first_name = 'Jane'
        c1_profile.last_name = 'Doe'
        c1_profile.location = 'NYC'
        c1_profile.save()

        c2 = User.objects.create_user(
            username='john', password='pw', email='john@test.com')

        c2.type = 'customer'
        c2.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 3)

        for item in response.data:
            self.assertEqual(item['type'], 'customer')
            self.assertNotEqual(item['username'], 'biz1')

        john_data = next(
            (item for item in response.data if item['username'] == 'john'), None)
        self.assertIsNotNone(john_data)
        self.assertEqual(john_data['first_name'], '')
        self.assertEqual(john_data['last_name'], '')

        self.assertNotIn('working_hours', john_data)
        self.assertNotIn('description', john_data)
        self.assertNotIn('email', john_data)
        self.assertNotIn('location', john_data)
