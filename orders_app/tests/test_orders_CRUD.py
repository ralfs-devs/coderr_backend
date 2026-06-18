"""Integration test modules checking data access restrictions, validation rules, and lifecycle mutations on orders."""

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

from offers_app.models import OfferDetails, Offers
from orders_app.models import Order

User = get_user_model()


class OrderListApiTest(APITestCase):
    """Tests checking data access restrictions and validation rules for listing orders.

    Attributes:
        user1 (User): A test consumer user entity.
        user2 (User): A test merchant business user entity.
        other_user (User): An unassociated user profile used to verify isolation boundaries.
        order (Order): A baseline operational task instance.
        url (str): Target routing configuration address for orders.
    """

    def setUp(self):
        """Prepares account records, mock authentications, and standalone baseline orders."""
        self.user1 = User.objects.create_user(
            username='u1', password='pw', email='u1@mail.de')
        self.user2 = User.objects.create_user(
            username='u2', password='pw', email='u2@mail.de')
        self.other_user = User.objects.create_user(
            username='u3', password='pw', email='u3@mail.de')

        self.order = Order.objects.create(
            customer_user=self.user1, business_user=self.user2,
            title='Logo Design', revisions=3, delivery_time_in_days=5,
            price=150.00, features=["Logo Design"], offer_type='basic'
        )
        self.url = reverse('orders')

    def test_get_orders_list_success(self):
        """Ensures an authenticated customer can successfully fetch their own order list items."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Logo Design')

    def test_get_orders_list_filter_security(self):
        """Verifies completely unrelated user accounts receive an empty set on order lists."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_orders_list_unauthenticated(self):
        """Guards endpoints against access attempts by unauthenticated network connections."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_orders_list_structure(self):
        """Validates response dictionaries against structural layout expectations and value types."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data[0]

        expected_keys = {
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "status", "created_at", "updated_at"
        }
        self.assertEqual(set(data.keys()), expected_keys)

        self.assertEqual(data['title'], 'Logo Design')
        self.assertIsInstance(data['features'], list)
        self.assertIsInstance(data['id'], int)
        self.assertIsInstance(data['created_at'], str)


class OrderCreateApiTest(APITestCase):
    """Handles verification and side effects checking during standard creation workflows.

    Attributes:
        business (User): A business user profile acting as the core owner.
        customer (User): A standard user profile acting as the prospective buyer.
        offer (Offers): The high-level framework asset profile.
        detail (OfferDetails): Specialized sub-tier blueprint configurations.
        url (str): Target routing configuration address for order collections.
    """

    def setUp(self):
        """Constructs target business entities and tier detail mock attributes."""
        self.business = User.objects.create_user(
            username='biz', password='pw', email='biz@mail.de', type='business')
        self.customer = User.objects.create_user(
            username='cust', password='pw', email='cust@mail.de')

        self.offer = Offers.objects.create(
            owner=self.business, title='Logo Design')
        self.detail = OfferDetails.objects.create(
            offer=self.offer, title='Logo Design', price=150.00,
            revisions=3, delivery_time_in_days=5, offer_type='basic'
        )

        self.detail.features = ["Logo Design", "Visitenkarten"]
        self.detail.save()

        self.url = reverse('orders')

    def test_create_order_success(self):
        """Validates successful entry instantiation when a customer inputs valid parameters."""
        self.client.force_authenticate(user=self.customer)
        data = {'offer_detail_id': self.detail.id}

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.title, 'Logo Design')
        self.assertEqual(order.price, 150.00)

    def test_create_order_unauthenticated(self):
        """Assures anonymous requests are rejected with a standard 401 error code."""
        data = {'offer_detail_id': self.detail.id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_invalid_data(self):
        """Confirms payload errors yield appropriate standard server rejection paths."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_not_found(self):
        """Checks handling behaviors if payload elements describe non-existent primary records."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            self.url, {'offer_detail_id': 999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderPatchApiTest(APITestCase):
    """Enforces authorization profiles during state-transition or tracking updates.

    Attributes:
        business (User): Authoritative vendor profile managing the project state.
        customer (User): Standard consumer user holding purchasing histories.
        offer (Offers): The underlying service item description mapping.
        detail (OfferDetails): Structural financial pricing configurations.
        order (Order): Active transactional pipeline track record element.
        url (str): Unique detail identifier endpoint lookup reference.
    """

    def setUp(self):
        """Initializes existing order entities across active production metrics."""
        self.business = User.objects.create_user(
            username='biz',
            type='business',
            password='pw1',
            email='biz@mail.de'
        )
        self.customer = User.objects.create_user(
            username='cust',
            type='customer',
            password='pw2',
            email='cust@mail.de',)

        self.offer = Offers.objects.create(
            owner=self.business, title='Logo Design')
        self.detail = OfferDetails.objects.create(
            offer=self.offer,
            title='Logo Design',
            price=150.00,
            revisions=3,
            delivery_time_in_days=5,
            offer_type='basic')

        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title='Logo Design',
            revisions=3,
            delivery_time_in_days=5,
            price=150.00,
            features=["Logo Design"],
            offer_type='basic',
            status='in_progress'
        )
        self.url = reverse('orders-detail', kwargs={'pk': self.order.id})

    def test_patch_status_success(self):
        """Guarantees the responsible business user can progress specific workflow states."""
        self.client.force_authenticate(user=self.business)
        response = self.client.patch(
            self.url, {'status': 'completed'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')

    def test_patch_status_forbidden_for_customer(self):
        """Restricts customer users from bypassing execution tracking fields."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(
            self.url, {'status': 'completed'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_status_forbidden_for_other_business(self):
        """Verifies completely independent business users cannot modify other providers orders."""
        other_business = User.objects.create_user(
            username='other_biz',
            type='business',
            password='pw3',
            email='other@mail.de'
        )
        self.client.force_authenticate(user=other_business)
        response = self.client.patch(
            self.url, {'status': 'completed'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_status_not_found(self):
        """Assures attempts directed at missing records produce standard missing errors."""
        self.client.force_authenticate(user=self.business)
        wrong_url = reverse('orders-detail', kwargs={'pk': 999})
        response = self.client.patch(
            wrong_url, {'status': 'completed'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderDeleteApiTest(APITestCase):
    """Verifies constraint profiles and destructive operations safety boundaries.

    Attributes:
        staff (User): Administrative clearance profile authorizing forced object deletions.
        business (User): Standard merchant account owning structural configurations.
        customer (User): Regular consumer account context holder.
        order (Order): Targeted system transaction instance planned for destruction.
        url (str): Destination routing indicator mapping individual instances.
    """

    def setUp(self):
        """Sets up operational administrative targets and tracking entries."""
        self.staff = User.objects.create_user(
            username='staff', type='business', password='pw', email='s@b.de')
        self.staff.is_staff = True
        self.staff.save()

        self.business = User.objects.create_user(
            username='biz', type='business', password='pw', email='b@b.de')
        self.customer = User.objects.create_user(
            username='cust', type='customer', password='pw', email='c@c.de')

        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title='Test Order',
            status='in_progress',
            delivery_time_in_days=3,
            price=100.0,
            revisions=1
        )
        self.url = reverse('orders-detail', kwargs={'pk': self.order.id})

    def test_delete_order_success(self):
        """Confirms that internal staff users can delete order records effectively."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

    def test_delete_order_forbidden_business(self):
        """Verifies business users cannot issue destructive delete actions."""
        self.client.force_authenticate(user=self.business)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_forbidden_customer(self):
        """Ensures customer users face full denial on order deletion attempts."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_not_found(self):
        """Asserts actions querying missing keys properly exit with a 404 response."""
        self.client.force_authenticate(user=self.staff)
        url = reverse('orders-detail', kwargs={'pk': 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
