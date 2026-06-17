from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

from offers_app.models import Offers, OfferDetails


User = get_user_model()


class SingleOfferDetailApiTest(APITestCase):

    def setUp(self):
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

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.detail.id)
        self.assertEqual(response.data['title'], self.detail.title)

    def test_get_detail_unauthenticated(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_detail_not_found(self):

        self.client.force_authenticate(user=self.user)
        invalid_url = reverse('single-offer-details', kwargs={'pk': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_offer_structure_with_user_id(self):
        # 1. Authentifizierung
        self.client.force_authenticate(user=self.user)

        # 2. Request an das ANGEBOT (nicht das Detail-Objekt)
        # Nutze hier die URL für das gesamte 'Offers'-Objekt
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # 3. Struktur-Validierung
        # Prüft, ob user == owner.id
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['title'], "Grafikdesign-Paket")

        # 4. Details-Liste prüfen
        self.assertIsInstance(data['details'], list)
        self.assertEqual(len(data['details']), 3)

        # Prüfe den Aufbau eines Detail-Items
        for detail in data['details']:
            self.assertIn('id', detail)
            self.assertIn('url', detail)
            self.assertTrue(detail['url'].startswith('http'))

        # 5. Preise prüfen
        self.assertEqual(data['min_price'], 50)
        self.assertEqual(data['min_delivery_time'], 5)
