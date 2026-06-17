from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from offers_app.models import Offers
from .test_base import BaseOfferTestMixin


class OfferDetailApiTest(BaseOfferTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('offers-detail', kwargs={'pk': self.offer.pk})

    def test_get_offer_detail_success(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.offer.id)
        self.assertEqual(response.data['title'], self.offer.title)
        self.assertIsInstance(response.data['details'], list)
        self.assertIn('min_price', response.data)

    def test_get_offer_detail_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offer_detail_not_found(self):
        self.client.force_authenticate(user=self.business_user)
        invalid_url = reverse('offers-detail', kwargs={'pk': 99999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferUpdateApiTest(BaseOfferTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        self.other_user = get_user_model().objects.create_user(
            username='hacker', password='password', email='hacker@test.de'
        )

    def test_patch_offer_success(self):
        self.client.force_authenticate(user=self.business_user)
        payload = {
            "title": "Updated Grafikdesign-Paket",
            "details": [
                {
                    "id": self.offer.details.first().id,
                    "title": "Basic Design Updated",
                    "offer_type": "basic"
                }
            ]
        }
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Updated Grafikdesign-Paket")
        self.assertEqual(response.data['details']
                         [0]['title'], "Basic Design Updated")

    def test_patch_offer_unauthenticated(self):
        response = self.client.patch(
            self.url, {"title": "Hack"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_offer_forbidden_wrong_user(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            self.url, {"title": "Hack"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_offer_not_found(self):
        self.client.force_authenticate(user=self.business_user)
        invalid_url = reverse('offers-detail', kwargs={'pk': 99999})
        response = self.client.patch(
            invalid_url, {"title": "Ghost"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferDeleteApiTest(BaseOfferTestMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('offers-detail', kwargs={'pk': self.offer.pk})

    def test_delete_offer_success(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offers.objects.filter(pk=self.offer.pk).exists())

    def test_delete_offer_unauthenticated(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_offer_forbidden(self):
        stranger = get_user_model().objects.create_user(
            username='stranger', password='password', email='s@s.com')
        self.client.force_authenticate(user=stranger)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offers.objects.filter(pk=self.offer.pk).exists())

    def test_delete_offer_not_found(self):
        self.client.force_authenticate(user=self.business_user)
        invalid_url = reverse('offers-detail', kwargs={'pk': 9999})
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
