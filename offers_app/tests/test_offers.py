from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from offers_app.models import Offers, OfferDetails
from .test_base import BaseOfferTestMixin

User = get_user_model()


class OffersListApiTest(APITestCase):

    def setUp(self):

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

        url = reverse('offers')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_offers_list_bad_request(self):
        url = reverse('offers')

        response = self.client.get(url, {'min_price': 'abc'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_success(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        if response.status_code == 400:
            print("\n--- VALIDERUNGSFEHLER (POST) ---")
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        offer_id = response.data['id']
        new_offer = Offers.objects.get(id=offer_id)

        self.assertEqual(new_offer.owner, self.business_user)
        self.assertEqual(new_offer.title, self.valid_payload['title'])

    def test_create_offer_unauthenticated_returns_401(self):

        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_non_business_user_returns_403(self):
        # 'j_doe' ist im setUp als normaler User ohne 'business'-Typ angelegt
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offers_list_structure(self):

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
