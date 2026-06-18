"""Tests isolating behavior and payload schemas of standalone package configurations."""

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

from offers_app.models import Offers, OfferDetails


User = get_user_model()


class SingleOfferDetailApiTest(APITestCase):
    """Test suite handling retrieval validation for explicit element packages.

    Attributes:
        user (User): A business user profile instance used to own and query resources.
        offer (Offers): A baseline core project offer instance.
        detail (OfferDetails): Individual sub-tier configuration metadata records.
        url (str): Target routing path location for specific detail endpoints.
    """

    def setUp(self):
        """Prepares database instances and populates multi-tiered test offers."""
        self.user = User.objects.create_user(
            username='testuser', type='business', password='pw', email='test@mail.de')
        self.offer = Offers.objects.create(
            owner=self.user, title='Grafikdesign-Paket')
        self.detail = OfferDetails.objects.create(
            offer=self.offer, title='Basic', revisions=2, delivery_time_in_days=5, price=50)
        OfferDetails.objects.create(
            offer=self.offer, title='Standard', revisions=4, delivery_time_in_days=10, price=100)
        OfferDetails.objects.create(
            offer=self.offer, title='Premium', revisions=6, delivery_time_in_days=15, price=150)
        self.url = reverse('single-offer-details',
                           kwargs={'pk': self.offer.pk})

    def test_get_detail_success(self):
        """Validates content attribute equivalence under authenticated execution."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.detail.id)
        self.assertEqual(response.data['title'], self.detail.title)

    def test_get_detail_unauthenticated(self):
        """Verifies that an unauthenticated request raises a 401 unauthorized status."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_detail_not_found(self):
        """Validates that hitting missing endpoints securely produces 404 outputs."""
        self.client.force_authenticate(user=self.user)
        invalid_url = reverse('single-offer-details', kwargs={'pk': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_offer_structure_with_user_id(self):
        """Validates complete hierarchy tree nested layouts, calculated mins, and schema formats."""
        self.client.force_authenticate(user=self.user)

        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['title'], "Grafikdesign-Paket")

        self.assertIsInstance(data['details'], list)
        self.assertEqual(len(data['details']), 3)

        for detail in data['details']:
            self.assertIn('id', detail)
            self.assertIn('url', detail)
            self.assertTrue(detail['url'].startswith('http'))

        self.assertEqual(data['min_price'], 50)
        self.assertEqual(data['min_delivery_time'], 5)
