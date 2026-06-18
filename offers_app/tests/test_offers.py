"""Integration test modules checking collection behavior on core endpoints."""

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from offers_app.models import Offers, OfferDetails


User = get_user_model()


class OffersListApiTest(APITestCase):
    """Test suite targeting group operations, registration restrictions, and collection formatting.

    Attributes:
        user (User): A test user with standard non-business consumer privileges.
        business_user (User): A test user explicitly assigned to the business segment profile.
        valid_payload (dict): Standardized, complete structural JSON payload for testing mutations.
        url (str): The routing lookup address mapped to list and creation endpoint collection hooks.
        offer (Offers): A baseline persistency record representing existing content elements.
    """

    def setUp(self):
        """Establishes target fixtures, base mock accounts, and standard payloads before runs."""
        self.user = User.objects.create_user(
            username='j_doe', email='jdoe@example.com', password='password')

        self.business_user = User.objects.create_user(
            username='biz_user',
            email='biz@example.com',
            password='password'
        )
        self.business_user.type = 'business'
        self.business_user.save()
        self.valid_payload = {
            "title": "Grafikdesign-Paket",
            "description": "Ein umfassendes Grafikdesign-Paket.",
            "details": [
                {"title": "Basic", "revisions": 1, "delivery_time_in_days": 1,
                 "price": 100, "features": [], "offer_type": "basic"},
                {"title": "Standard", "revisions": 2, "delivery_time_in_days": 2,
                 "price": 200, "features": [], "offer_type": "standard"},
                {"title": "Premium", "revisions": 3, "delivery_time_in_days": 3,
                 "price": 300, "features": [], "offer_type": "premium"}
            ]
        }
        self.url = reverse('offers')

        self.offer = Offers.objects.create(
            owner=self.user,
            title="Website Design",
            description="Professionelles Website-Design..."
        )

        OfferDetails.objects.create(offer=self.offer, title="Basic", revisions=2,
                                    delivery_time_in_days=7, price=100, offer_type='basic')
        OfferDetails.objects.create(offer=self.offer, title="Standard", revisions=5,
                                    delivery_time_in_days=14, price=250, offer_type='standard')
        OfferDetails.objects.create(offer=self.offer, title="Premium", revisions=10,
                                    delivery_time_in_days=21, price=500, offer_type='premium')

    def test_get_offers_list_status_200(self):
        """Verifies that an unauthenticated client receives HTTP 200 OK when requesting listings."""
        url = reverse('offers')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_offers_list_bad_request(self):
        """Verifies that improper input inside filter arguments raises a 400 validation response."""
        url = reverse('offers')

        response = self.client.get(url, {'min_price': 'abc'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_success(self):
        """Validates successful insertion sequences when triggered by matching business accounts."""
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        offer_id = response.data['id']
        new_offer = Offers.objects.get(id=offer_id)

        self.assertEqual(new_offer.owner, self.business_user)
        self.assertEqual(new_offer.title, self.valid_payload['title'])

    def test_create_offer_unauthenticated_returns_401(self):
        """Confirms that anonymous client submission attempts trigger instant 401 rejections."""
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_non_business_user_returns_403(self):
        """Ensures non-business customer types are restricted with a 403 authorization block."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offers_list_structure(self):
        """Tests that response objects match standard pagination architecture specifications."""
        response = self.client.get(self.url, {'page_size': 6})
        self.assertIn('results', response.data,
                      f"Antwort ist nicht paginiert: {response.data}")
        first_offer = response.data['results'][0]

        self.assertIn('id', first_offer)
        self.assertIn('details', first_offer)
        self.assertIn('user_details', first_offer)
        self.assertIn('min_price', first_offer)

        self.assertIsInstance(first_offer['details'], list)
        self.assertIsInstance(first_offer['user_details'], dict)

        expected_user_keys = {'first_name', 'last_name', 'username'}
        self.assertTrue(expected_user_keys.issubset(
            first_offer['user_details'].keys()))

        if first_offer['details']:
            self.assertIn('url', first_offer['details'][0])
