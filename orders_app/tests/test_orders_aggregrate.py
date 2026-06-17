from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from orders_app.models import Order

User = get_user_model()


class OrderCountApiTest(APITestCase):
    def setUp(self):
        self.business = User.objects.create_user(
            username='biz', type='business', password='pw', email='biz@test.de'
        )
        self.customer = User.objects.create_user(
            username='cust', type='customer', password='pw', email='cust@test.de'
        )
        self.client.force_authenticate(user=self.business)

        for _ in range(2):
            Order.objects.create(
                customer_user=self.customer, business_user=self.business,
                status='in_progress', title='T', delivery_time_in_days=1,
                price=1, revisions=1
            )

    def test_order_count_success(self):
        url = reverse('ord-proc_cnt', kwargs={'pk': self.business.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 2)

    def test_order_count_not_found(self):
        url = reverse('ord-proc_cnt', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CompletedOrderCountApiTest(APITestCase):
    def setUp(self):
        self.business = User.objects.create_user(
            username='biz', type='business', password='pw', email='biz@test.de'
        )
        self.customer = User.objects.create_user(
            username='cust', type='customer', password='pw', email='cust@test.de'
        )
        self.client.force_authenticate(user=self.business)

        for _ in range(3):
            Order.objects.create(
                customer_user=self.customer, business_user=self.business,
                status='completed', title='T', delivery_time_in_days=1,
                price=1, revisions=1
            )

    def test_completed_order_count_success(self):
        url = reverse('ord-cpl_cnt', kwargs={'pk': self.business.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 3)

    def test_completed_order_count_not_found(self):
        url = reverse('ord-cpl_cnt', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
