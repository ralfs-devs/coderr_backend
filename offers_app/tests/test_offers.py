"""Integration test modules checking collection behavior on core endpoints."""

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from offers_app.models import Offers, OfferDetails


User = get_user_model()


class OffersListApiTest(APITestCase):
    """Test suite targeting 
    group operations, 
    registration restrictions
    and collection formatting.

    Attributes:
        user (User): 
            A test user with standard non-business consumer privileges.
        business_user (User): 
            A test user explicitly assigned to the business segment profile.
        valid_payload (dict): 
            Standardized, complete structural JSON payload 
                for testing mutations.
        url (str): 
            The routing lookup address.
        offer (Offers): 
            A baseline persistency record
                representing existing content elements.
    """

    def setUp(self):
        """Establishes target fixtures, base mock accounts
            and standard payloads before runs."""
        self.user = User.objects.create_user(
            username='j_doe',
            email='jdoe@example.com',
            password='password',
            type='customer')

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
                {"title": "Basic",
                 "revisions": 1,
                 "delivery_time_in_days": 1,
                 "price": 100,
                 "features": [],
                 "offer_type": "basic"},
                {"title": "Standard",
                 "revisions": 2,
                 "delivery_time_in_days": 2,
                 "price": 200,
                 "features": [],
                 "offer_type": "standard"},
                {"title": "Premium",
                 "revisions": 3,
                 "delivery_time_in_days": 3,
                 "price": 300,
                 "features": [],
                 "offer_type": "premium"}
            ]
        }
        self.url = reverse('offers')

        self.offer = Offers.objects.create(
            owner=self.user,
            title="Website Design",
            description="Professionelles Website-Design..."
        )

        OfferDetails.objects.create(offer=self.offer,
                                    title="Basic",
                                    revisions=2,
                                    delivery_time_in_days=7,
                                    price=100,
                                    offer_type='basic')
        OfferDetails.objects.create(offer=self.offer,
                                    title="Standard",
                                    revisions=5,
                                    delivery_time_in_days=14,
                                    price=250,
                                    offer_type='standard')
        OfferDetails.objects.create(offer=self.offer,
                                    title="Premium",
                                    revisions=10,
                                    delivery_time_in_days=21,
                                    price=500,
                                    offer_type='premium')

    def test_get_offers_list_status_200(self):
        """Verifies that an unauthenticated client 
            receives HTTP 200 OK when requesting listings."""
        url = reverse('offers')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_offers_list_bad_request(self):
        """Verifies that improper input inside filter arguments 
            raises a 400 validation response."""
        url = reverse('offers')

        response = self.client.get(url, {'min_price': 'abc'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_success(self):
        """Validates successful insertion sequences 
            when triggered by matching business accounts."""
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        offer_id = response.data['id']
        new_offer = Offers.objects.get(id=offer_id)

        self.assertEqual(new_offer.owner, self.business_user)
        self.assertEqual(new_offer.title, self.valid_payload['title'])

    def test_create_offer_unauthenticated_returns_401(self):
        """Confirms that anonymous client submission attempts 
            trigger instant 401 rejections."""
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_non_business_user_returns_403(self):
        """Ensures non-business customer types 
        are restricted with a 403 authorization block."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offers_list_structure(self):
        """Tests that response objects match 
        standard pagination architecture specifications."""
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
            self.assertIn('id', first_offer['details'][0])

    def test_offers_list_exact_structure_and_order(self):
        """Verifies that the paginated response 
        matches the exact key sequence, content types
            and has no extra fields."""
        response = self.client.get(self.url, {'page_size': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        expected_root_keys = ['count', 'next', 'previous', 'results']
        self.assertEqual(list(response_data.keys()), expected_root_keys)

        self.assertIsInstance(response_data['count'], int)
        self.assertTrue(response_data['next'] is None or isinstance(
            response_data['next'], str))
        self.assertTrue(response_data['previous'] is None or isinstance(
            response_data['previous'], str))
        self.assertIsInstance(response_data['results'], list)

        if response_data['results']:
            offer = response_data['results'][0]

            expected_offer_keys = [
                'id', 'user', 'title', 'image', 'description',
                'created_at', 'updated_at', 'details', 'min_price',
                'min_delivery_time', 'user_details'
            ]

            self.assertEqual(
                list(offer.keys()),
                expected_offer_keys,
                msg=f"Unexpected Fields in details: {list(offer.keys())}"
            )

            self.assertIsInstance(offer['id'], int)
            self.assertIsInstance(offer['user'], int)
            self.assertIsInstance(offer['title'], str)
            self.assertTrue(
                offer['image'] is None or isinstance(offer['image'], str))
            self.assertIsInstance(offer['description'], str)
            self.assertIsInstance(offer['created_at'], str)
            self.assertIsInstance(offer['updated_at'], str)
            self.assertIsInstance(offer['min_price'], (int, float))
            self.assertIsInstance(offer['min_delivery_time'], int)

            self.assertIsInstance(offer['details'], list)
            if offer['details']:
                detail = offer['details'][0]
                expected_detail_keys = ['id', 'url']
                self.assertEqual(
                    list(detail.keys()),
                    expected_detail_keys,
                    msg=("Unexpected fields in details "
                         f"(e.g. 'url'): {list(detail.keys())}")
                )
                self.assertIsInstance(detail['id'], int)

            self.assertIsInstance(offer['user_details'], dict)
            expected_user_keys = ['first_name', 'last_name', 'username']
            self.assertEqual(
                list(offer['user_details'].keys()),
                expected_user_keys,
                msg=(f"Unerwartete oder falsch sortierte Felder in "
                     f"user_details: {list(offer['user_details'].keys())}")
            )
            self.assertIsInstance(offer['user_details']['first_name'], str)
            self.assertIsInstance(offer['user_details']['last_name'], str)
            self.assertIsInstance(offer['user_details']['username'], str)

    def test_offers_list_filter_min_price_success_returns_json(self):
        """Verifies that a valid min_price filter query 
        returns HTTP 200 OK and a valid JSON response."""
        response = self.client.get(
            self.url, {'min_price': 75, 'page_size': 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')

        response_data = response.json()
        self.assertIn('results', response_data)

    def test_offers_list_filter_min_price_invalid_returns_bad_request(self):
        """Ensures that an invalid non-numeric min_price value safely 
        returns HTTP 400 Bad Request as JSON."""
        response = self.client.get(self.url, {'min_price': 'invalid_string'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_offers_list_filter_max_delivery_time_success_returns_json(self):
        """Verifies that a valid max_delivery_time filter query 
        returns HTTP 200 OK and a valid JSON response."""
        response = self.client.get(self.url, {'max_delivery_time': 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')

        response_data = response.json()
        self.assertIn('results', response_data)

    def test_offers_list_filter_max_deliv_time_inv_ret_bad_request(self):
        """Ensures that an invalid non-numeric max_delivery_time value safely 
        returns HTTP 400 Bad Request as JSON."""
        response = self.client.get(
            self.url, {'max_delivery_time': 'not_a_number'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_offers_list_filter_creator_id_success_returns_json(self):
        """Verifies that a valid creator_id filter query 
        returns HTTP 200 OK and a valid JSON response."""
        response = self.client.get(self.url, {'creator_id': self.user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')

        response_data = response.json()
        self.assertIn('results', response_data)

    def test_offers_list_filter_creator_id_invalid_returns_bad_request(self):
        """Ensures that an invalid non-numeric creator_id value safely 
        returns HTTP 400 Bad Request as JSON."""
        response = self.client.get(self.url, {'creator_id': 'invalid_user'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_offers_list_filter_search_matches_title(self):
        """Verifies that the search filter correctly 
        returns records matching the title text."""
        response = self.client.get(self.url, {'search': 'Website Design'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')

        response_data = response.json()

        self.assertTrue(len(response_data['results']) > 0)
        self.assertEqual(response_data['results']
                         [0]['title'], 'Website Design')

    def test_offers_list_filter_search_no_match_returns_empty(self):
        """Ensures that a search query with no matching text fields 
        returns an empty result list."""
        response = self.client.get(
            self.url, {'search': 'NonExistentString12345'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        self.assertEqual(len(response_data['results']), 0)

    def test_create_offer_by_non_business_user_returns_403(self):
        """Validates that a customer profile 
        is barred from producing a new offer collection."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/offers/', self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
