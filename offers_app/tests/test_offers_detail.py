"""Tests targeting access control and single entry modifications on offer details."""

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from offers_app.models import Offers
from offers_app.tests.test_base import BaseOfferTestMixin


class OfferDetailApiTest(BaseOfferTestMixin, APITestCase):
    """Test suite focused on detail tracking and view limitations.

    Attributes:
        url (str): The target endpoint URL for individual offer detail records.
    """

    def setUp(self):
        """Initializes configuration references through mixin parent setups."""
        super().setUp()
        self.url = reverse('offers-detail', kwargs={'pk': self.offer.pk})

    def test_get_offer_detail_success(self):
        """Confirms accurate model extraction format parsing on target hits."""
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.offer.id)
        self.assertEqual(response.data['title'], self.offer.title)
        self.assertIsInstance(response.data['details'], list)
        self.assertIn('min_price', response.data)

    def test_get_offer_detail_unauthenticated(self):
        """Verifies safe rejection blocking sequence if token context parameters are omitted."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offer_detail_not_found(self):
        """Ensures that query inputs targetting missing unique primary keys raise a 404 error."""
        self.client.force_authenticate(user=self.business_user)
        invalid_url = reverse('offers-detail', kwargs={'pk': 99999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferUpdateApiTest(BaseOfferTestMixin, APITestCase):
    """Test case handling evaluation paths during partial modification instructions.

    Attributes:
        url (str): The target endpoint URL for individual offer detail records.
        other_user (User): An alternate user profile instance used to test permission breaches.
    """

    def setUp(self):
        """Appends alternate user configurations into basic parent setup environments."""
        super().setUp()
        self.url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        self.other_user = get_user_model().objects.create_user(
            username='hacker', password='password', email='hacker@test.de'
        )

    def test_patch_offer_success(self):
        """Validates attribute adjustments when invoked by authentic profile authors."""
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

    def test_patch_offer_partial_details_updates_successfully(self):
        """Validates that a partial PATCH request 
        successfully updates a specific detail tier."""
        self.client.force_authenticate(user=self.business_user)
        detail_url = reverse('offers-detail', kwargs={'pk': self.offer.id})

        payload = {
            "title": "Updated Grafikdesign-Paket",
            "details": [
                {
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": 120,
                    "features": ["Logo Design", "Flyer"],
                    "offer_type": "basic"
                }
            ]
        }

        response = self.client.patch(detail_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(response_data["title"], "Updated Grafikdesign-Paket")
        self.assertEqual(len(response_data["details"]), 3)

        for detail in response_data["details"]:
            self.assertIn("id", detail)
            self.assertIsInstance(detail["id"], int)
            self.assertNotIn("url", detail)

        basic_tier = next(
            d for d in response_data["details"] if d["offer_type"] == "basic")
        self.assertEqual(basic_tier["title"], "Basic Design Updated")
        self.assertEqual(basic_tier["revisions"], 3)
        self.assertEqual(basic_tier["price"], 120)

    def test_patch_offer_unauthenticated(self):
        """Blocks modifications when credentials parameters 
        are missing from request scope headers."""
        response = self.client.patch(
            self.url, {"title": "Hack"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_offer_forbidden_wrong_user(self):
        """Throws explicit 403 exceptions when unauthorized 
        users attempt resource mutations."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            self.url, {"title": "Hack"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_offer_not_found(self):
        """Validates that update calls 
        to non-existent primary keys yield a 404 response."""
        self.client.force_authenticate(user=self.business_user)
        invalid_url = reverse('offers-detail', kwargs={'pk': 99999})
        response = self.client.patch(
            invalid_url, {"title": "Ghost"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_fails_if_offer_type_is_missing_in_details(self):
        """Verify that a PATCH request returns 400 
        if the offer_type is missing in the details list.

        Args:
            None

        Returns:
            None
        """
        self.client.login(username='biz_man', password='password')

        url = f"/api/offers/{self.offer.id}/"

        payload = {
            "title": "Updated Grafikdesign-Paket 288",
            "details": [
                {
                    "title": "Basic Design Updated 71",
                    "revisions": 10,
                    "delivery_time_in_days": 4,
                    "price": 465,
                    "features": [
                        "Dillan",
                        "Vito"
                    ]
                }
            ]
        }

        response = self.client.patch(url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OfferDeleteApiTest(BaseOfferTestMixin, APITestCase):
    """Verifies permission validations and database side-effects 
    of deletion requests.

    Attributes:
        url (str): The target endpoint URL for individual offer detail records.
    """

    def setUp(self):
        """Sets up the initial state for deletion tracking routines."""
        super().setUp()
        self.url = reverse('offers-detail', kwargs={'pk': self.offer.pk})

    def test_delete_offer_success(self):
        """Asserts proper instance purging operations 
        by verified master entity owners."""
        self.client.force_authenticate(user=self.business_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offers.objects.filter(pk=self.offer.pk).exists())

    def test_delete_offer_unauthenticated(self):
        """Ensures anonymous drop operations fail 
        without removing entries from records."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_offer_forbidden(self):
        """Guards and confirms that 
        external profiles cannot trigger deletion sequences."""
        stranger = get_user_model().objects.create_user(
            username='stranger', password='password', email='s@s.com')
        self.client.force_authenticate(user=stranger)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offers.objects.filter(pk=self.offer.pk).exists())

    def test_delete_offer_not_found(self):
        """Confirms 404 error management behaviors 
        when target items do not exist."""
        self.client.force_authenticate(user=self.business_user)
        invalid_url = reverse('offers-detail', kwargs={'pk': 9999})
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
