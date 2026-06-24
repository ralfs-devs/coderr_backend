"""Unit tests for the aggregation endpoints."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from reviews_app.models import Reviews
from offers_app.models import Offers

User = get_user_model()


class BaseInfoApiTests(APITestCase):
    """Test suite for the BaseInfoView metrics endpoint."""

    def setUp(self):
        """Sets up test users, offers
            and reviews data before each test execution."""
        self.url = reverse('base_info')

        self.biz1 = User.objects.create_user(
            username='biz1',
            type='business',
            password='pw1',
            email='b1@b.com')
        self.biz2 = User.objects.create_user(
            username='biz2',
            type='business',
            password='pw2',
            email='b2@b.com')
        self.cust1 = User.objects.create_user(
            username='cust1',
            type='customer',
            password='pw3',
            email='c1@c.com')
        self.cust2 = User.objects.create_user(
            username='cust2',
            type='customer',
            password='pw4',
            email='c2@c.com')
        Offers.objects.create(
            title='O1', owner=self.biz1, description='Test 1')
        Offers.objects.create(
            title='O2', owner=self.biz1, description='Test 2')
        Offers.objects.create(
            title='O3', owner=self.biz1, description='Test 3')

        Reviews.objects.create(
            rating=5, business_user=self.biz1, reviewer=self.cust1)
        Reviews.objects.create(
            rating=4, business_user=self.biz1, reviewer=self.cust2)
        Reviews.objects.create(
            rating=3, business_user=self.biz2, reviewer=self.cust2)

    def test_base_info_success_status(self):
        """Verifies that the endpoint returns a 200 OK status code."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_aggregation(self):
        """Validates that the database values 
            are aggregated and calculated correctly."""
        response = self.client.get(self.url)

        self.assertEqual(response.data['review_count'], 3)
        self.assertEqual(response.data['average_rating'], 4.0)
        self.assertEqual(response.data['business_profile_count'], 2)
        self.assertEqual(response.data['offer_count'], 3)

    def test_empty_data(self):
        """Ensures the endpoint gracefully falls back to zeroed values 
            when database tables are empty."""
        Reviews.objects.all().delete()
        Offers.objects.all().delete()
        User.objects.filter(type='business').delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review_count'], 0)
        self.assertEqual(response.data['average_rating'], 0.0)
        self.assertEqual(response.data['business_profile_count'], 0)
        self.assertEqual(response.data['offer_count'], 0)
