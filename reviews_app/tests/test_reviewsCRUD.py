"""
Integration tests verifying full CRUD operations, validation rules 
and access control for customer reviews.
"""

from django.contrib.auth import get_user_model

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from reviews_app.models import Reviews

User = get_user_model()


class ReviewsCRUDTests(APITestCase):
    """
    Functional validation tests covering complete life cycle sequences
        and access layers for reviews records.

    Attributes:
        biz_user (User): 
            Reference profile entity representing the service provider target.
        cust_user (User): 
            Baseline context profile acting as the original author of records.
        other_cust_user (User):
            Secondary profile workspace 
                representing distinct third-party requests.
        review (Reviews): 
            Pre-populated reference database entity 
                mapped to baseline profiles.
        list_url (str):
            Reversible operational route mapped to the collection endpoints.
    """

    def setUp(self):
        """Pre-configures test environments,
            generating target user entities and tracking endpoints."""
        self.biz_user = User.objects.create_user(
            username='biz1',
            email='biz@test.de',
            password='pw',
            type='business')
        self.cust_user = User.objects.create_user(
            username='cust1',
            email='cust@test.de',
            password='pw',
            type='customer')
        self.other_cust_user = User.objects.create_user(
            username='cust2',
            email='other@test.de',
            password='pw',
            type='customer')

        self.review = Reviews.objects.create(
            business_user=self.biz_user, reviewer=self.cust_user,
            rating=4, description="Original"
        )
        self.list_url = reverse('reviews')

    def test_get_reviews_list(self):
        """Ensures verified authenticated profiles retrieve a formatted List
            tracking active records."""
        self.client.force_authenticate(user=self.cust_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_get_reviews_unauthorized(self):
        """Confirms unauthenticated connection attempts 
            are blocked from entering public list layers."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_review_success(self):
        """Verifies that an independent profile can store 
            a new structured review against valid target entities."""
        self.client.force_authenticate(user=self.other_cust_user)
        data = {"business_user": self.biz_user.id,
                "rating": 5, "description": "Neu"}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_review_duplicate_forbidden(self):
        """
        Confirms double submission attempts against identical target entities
            drop with client exception flags.
        """
        self.client.force_authenticate(user=self.cust_user)
        data = {"business_user": self.biz_user.id,
                "rating": 5, "description": "Doppelt"}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_success(self):
        """Validates that resource owner can execute 
            structural changes across single entity attributes."""
        self.client.force_authenticate(user=self.cust_user)
        data = {"rating": 5, "description": "Update"}
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_review_forbidden_non_owner(self):
        """Blocks external unlinked profiles from updating fields 
            belonging to distinct record owners."""
        self.client.force_authenticate(user=self.other_cust_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.patch(url, {"rating": 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_not_found(self):
        """Confirms bad tracking signatures 
            yield standard missing element data flags upon updating."""
        self.client.force_authenticate(user=self.cust_user)
        url = reverse('reviews-detail', kwargs={'pk': 999})
        response = self.client.patch(url, {"rating": 5})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_review_success(self):
        """Confirms resource authors possess clearance
            to scrub distinct records from active database tables."""
        self.client.force_authenticate(user=self.cust_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_review_forbidden_non_owner(self):
        """Ensures access managers block unauthorized deletion targets 
            requested by foreign profile headers."""
        self.client.force_authenticate(user=self.other_cust_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_not_found(self):
        """Confirms attempts to wipe unmapped identities terminate
            with common missing resource structures."""
        self.client.force_authenticate(user=self.cust_user)
        url = reverse('reviews-detail', kwargs={'pk': 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_reviews_filtering_and_ordering(self):
        """Validates network query operations containing explicit parameters
            return ordered query arrays."""
        self.client.force_authenticate(user=self.cust_user)
        response = self.client.get(
            f'{self.list_url}?business_user_id={self.biz_user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response_ordered = self.client.get(f'{self.list_url}?ordering=rating')
        self.assertEqual(response_ordered.status_code, status.HTTP_200_OK)

    def test_post_review_full_data(self):
        """Verifies deep dictionary payloads write structural property fields 
            without missing structural values."""
        self.client.force_authenticate(user=self.other_cust_user)
        data = {"business_user": self.biz_user.id,
                "rating": 5, "description": "Alles war toll!"}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)

    def test_patch_partial_update(self):
        """Ensures validation blocks apply cleanly
            during partial parameter update requests from authors."""
        self.client.force_authenticate(user=self.cust_user)
        data = {"rating": 5, "description": "Noch besser als erwartet!"}
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)

    def test_delete_review(self):
        """Re-evaluates system consistency limits 
        across complete element removal sequences."""
        self.client.force_authenticate(user=self.cust_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_reviews_filters_by_business_user(self):
        """Verify that the list endpoint returns 
            all matching business_user records and excludes others.

        Args:
            None

        Returns:
            None
        """
        self.client.force_authenticate(user=self.cust_user)

        third_cust = User.objects.create_user(
            username='cust3_unique_for_biz_test',
            email='cust3_unique_biz@test.de',
            password='pw',
            type='customer'
        )

        Reviews.objects.create(
            business_user=self.biz_user,
            reviewer=third_cust,
            rating=5,
            description="Second unique review for target business"
        )

        second_biz = User.objects.create_user(
            username='biz2_unique_for_filter_test',
            email='biz2_unique_filter@test.de',
            password='pw',
            type='business'
        )

        Reviews.objects.create(
            business_user=second_biz,
            reviewer=self.other_cust_user,
            rating=3,
            description="Review for a different business"
        )

        target_id = self.biz_user.id
        response = self.client.get(self.list_url, {"business_user": target_id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data
        if "results" in results:
            results = results["results"]

        expected_reviews = Reviews.objects.filter(business_user_id=target_id)
        expected_dict = {review.id: review for review in expected_reviews}

        self.assertEqual(len(results), len(expected_dict))

        for review_data in results:
            review_id = review_data["id"]
            self.assertIn(review_id, expected_dict)

            db_review = expected_dict[review_id]
            self.assertEqual(
                review_data["business_user"], db_review.business_user_id)
            self.assertEqual(review_data["reviewer"], db_review.reviewer_id)
            self.assertEqual(review_data["rating"], db_review.rating)
            self.assertEqual(review_data["description"], db_review.description)

    def test_list_reviews_filters_by_reviewer(self):
        """Verify that the list endpoint returns 
            all matching reviewer_id records and excludes others.

        Args:
            None

        Returns:
            None
        """
        self.client.force_authenticate(user=self.cust_user)

        second_biz = User.objects.create_user(
            username='biz_unique_for_filter_test',
            email='biz_unique_filter@test.de',
            password='pw',
            type='business'
        )

        Reviews.objects.create(
            business_user=second_biz,
            reviewer=self.cust_user,
            rating=5,
            description="Second unique review by target reviewer"
        )

        Reviews.objects.create(
            business_user=self.biz_user,
            reviewer=self.other_cust_user,
            rating=3,
            description="Review by a different reviewer"
        )

        target_id = self.cust_user.id
        response = self.client.get(self.list_url, {"reviewer_id": target_id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data
        if "results" in results:
            results = results["results"]

        expected_reviews = Reviews.objects.filter(reviewer_id=target_id)
        expected_dict = {review.id: review for review in expected_reviews}

        self.assertEqual(len(results), len(expected_dict))

        for review_data in results:
            review_id = review_data["id"]
            self.assertIn(review_id, expected_dict)

            db_review = expected_dict[review_id]
            self.assertEqual(
                review_data["business_user"], db_review.business_user_id)
            self.assertEqual(review_data["reviewer"], db_review.reviewer_id)
            self.assertEqual(review_data["rating"], db_review.rating)
            self.assertEqual(review_data["description"], db_review.description)
