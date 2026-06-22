from rest_framework.test import APITestCase
from offers_app.models import Offers, OfferDetails
from profiles_app.models import Profile
from user_auth_app.models import User


class BaseOfferTestMixin(APITestCase):

    from rest_framework.test import APITestCase


class BaseOfferTestMixin(APITestCase):

    @classmethod
    def setUpTestData(cls):
        """Sets up the initial test data for all inheriting test cases."""
        cls.business_user = User.objects.create_user(
            username='biz_man',
            email='biz@test.de',
            password='password'
        )
        cls.business_user.type = 'business'
        cls.business_user.save()

        for i in range(93):
            offer = Offers.objects.create(
                owner=cls.business_user,
                title=f"Angebot {i}",
                description="Testbeschreibung"
            )

            OfferDetails.objects.create(
                offer=offer,
                title="Basic",
                price=100 + i,
                delivery_time_in_days=1 + (i % 10),
                offer_type='basic',
                revisions=1 + (i % 3)
            )

            OfferDetails.objects.create(
                offer=offer,
                title="Standard",
                price=150 + i,
                delivery_time_in_days=2 + (i % 10),
                offer_type='standard',
                revisions=2 + (i % 3)
            )

            OfferDetails.objects.create(
                offer=offer,
                title="Premium",
                price=200 + i,
                delivery_time_in_days=3 + (i % 10),
                offer_type='premium',
                revisions=3 + (i % 3)
            )
        cls.offer = offer
