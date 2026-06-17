# from rest_framework.reverse import reverse
# from rest_framework.test import APITestCase
# from rest_framework import status

# from django.contrib.auth import get_user_model
# from ..models import Reviews

# User = get_user_model()


# class ReviewsCRUDTests(APITestCase):
#     def setUp(self):

#         self.biz_user = User.objects.create_user(
#             username='biz1', email='biz@test.de', password='pw', type='business')
#         self.cust_user = User.objects.create_user(
#             username='cust1', email='cust@test.de', password='pw', type='customer')
#         self.other_cust_user = User.objects.create_user(
#             username='cust2', email='other@test.de', password='pw', type='customer')

#         self.review = Reviews.objects.create(
#             business_user=self.biz_user, reviewer=self.cust_user,
#             rating=4, description="Original"
#         )
#         self.list_url = reverse('reviews')

#     def test_get_reviews_list(self):
#         self.client.force_authenticate(user=self.cust_user)
#         response = self.client.get('/api/reviews/')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIsInstance(response.data, list)

#     def test_get_reviews_unauthorized(self):
#         response = self.client.get('/api/reviews/')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_post_review_success(self):
#         self.client.force_authenticate(user=self.other_cust_user)
#         data = {"business_user": self.biz_user.id,
#                 "rating": 5, "description": "Neu"}
#         response = self.client.post('/api/reviews/', data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_post_review_duplicate_forbidden(self):
#         self.client.force_authenticate(user=self.cust_user)
#         data = {"business_user": self.biz_user.id,
#                 "rating": 5, "description": "Doppelt"}
#         response = self.client.post('/api/reviews/', data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_patch_review_success(self):
#         self.client.force_authenticate(user=self.cust_user)
#         data = {"rating": 5, "description": "Update"}
#         response = self.client.patch(
#             f'/api/reviews/{self.review.id}/', data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_patch_review_forbidden_non_owner(self):
#         self.client.force_authenticate(user=self.other_cust_user)
#         response = self.client.patch(
#             f'/api/reviews/{self.review.id}/', {"rating": 1})
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_patch_review_not_found(self):
#         self.client.force_authenticate(user=self.cust_user)
#         response = self.client.patch('/api/reviews/999/', {"rating": 5})
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_delete_review_success(self):
#         self.client.force_authenticate(user=self.cust_user)
#         response = self.client.delete(f'/api/reviews/{self.review.id}/')
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_delete_review_forbidden_non_owner(self):
#         self.client.force_authenticate(user=self.other_cust_user)
#         response = self.client.delete(f'/api/reviews/{self.review.id}/')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_delete_review_not_found(self):
#         self.client.force_authenticate(user=self.cust_user)
#         response = self.client.delete('/api/reviews/999/')
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_get_reviews_filtering_and_ordering(self):
#         self.client.force_authenticate(user=self.cust_user)

#         response = self.client.get(
#             f'/api/reviews/?business_user_id={self.biz_user.id}')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#         response_ordered = self.client.get('/api/reviews/?ordering=rating')
#         self.assertEqual(response_ordered.status_code, status.HTTP_200_OK)

#     def test_post_review_full_data(self):
#         self.client.force_authenticate(user=self.other_cust_user)
#         data = {"business_user": self.biz_user.id,
#                 "rating": 5, "description": "Alles war toll!"}
#         response = self.client.post('/api/reviews/', data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['rating'], 5)

#     def test_patch_partial_update(self):
#         self.client.force_authenticate(user=self.cust_user)
#         data = {"rating": 5, "description": "Noch besser als erwartet!"}
#         response = self.client.patch(
#             f'/api/reviews/{self.review.id}/', data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['rating'], 5)

#     def test_delete_review(self):
#         self.client.force_authenticate(user=self.cust_user)
#         response = self.client.delete(f'/api/reviews/{self.review.id}/')
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import Reviews

User = get_user_model()


class ReviewsCRUDTests(APITestCase):
    def setUp(self):
        self.biz_user = User.objects.create_user(
            username='biz1', email='biz@test.de', password='pw', type='business')
        self.cust_user = User.objects.create_user(
            username='cust1', email='cust@test.de', password='pw', type='customer')
        self.other_cust_user = User.objects.create_user(
            username='cust2', email='other@test.de', password='pw', type='customer')

        self.review = Reviews.objects.create(
            business_user=self.biz_user, reviewer=self.cust_user,
            rating=4, description="Original"
        )
        self.list_url = reverse('reviews')

    def test_get_reviews_list(self):
        self.client.force_authenticate(user=self.cust_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_get_reviews_unauthorized(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_review_success(self):
        self.client.force_authenticate(user=self.other_cust_user)
        data = {"business_user": self.biz_user.id,
                "rating": 5, "description": "Neu"}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_review_duplicate_forbidden(self):
        self.client.force_authenticate(user=self.cust_user)
        data = {"business_user": self.biz_user.id,
                "rating": 5, "description": "Doppelt"}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_success(self):
        self.client.force_authenticate(user=self.cust_user)
        data = {"rating": 5, "description": "Update"}
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_review_forbidden_non_owner(self):
        self.client.force_authenticate(user=self.other_cust_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.patch(url, {"rating": 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_not_found(self):
        self.client.force_authenticate(user=self.cust_user)
        url = reverse('reviews-detail', kwargs={'pk': 999})
        response = self.client.patch(url, {"rating": 5})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_review_success(self):
        self.client.force_authenticate(user=self.cust_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_review_forbidden_non_owner(self):
        self.client.force_authenticate(user=self.other_cust_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_not_found(self):
        self.client.force_authenticate(user=self.cust_user)
        url = reverse('reviews-detail', kwargs={'pk': 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_reviews_filtering_and_ordering(self):
        self.client.force_authenticate(user=self.cust_user)
        response = self.client.get(
            f'{self.list_url}?business_user_id={self.biz_user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response_ordered = self.client.get(f'{self.list_url}?ordering=rating')
        self.assertEqual(response_ordered.status_code, status.HTTP_200_OK)

    def test_post_review_full_data(self):
        self.client.force_authenticate(user=self.other_cust_user)
        data = {"business_user": self.biz_user.id,
                "rating": 5, "description": "Alles war toll!"}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)

    def test_patch_partial_update(self):
        self.client.force_authenticate(user=self.cust_user)
        data = {"rating": 5, "description": "Noch besser als erwartet!"}
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)

    def test_delete_review(self):
        self.client.force_authenticate(user=self.cust_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
