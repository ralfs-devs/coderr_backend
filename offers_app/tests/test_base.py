from rest_framework.test import APITestCase
from offers_app.models import Offers, OfferDetails
from profiles_app.models import Profile
from user_auth_app.models import User


class BaseOfferTestMixin(APITestCase):

    @classmethod
    def setUpTestData(cls):

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
        cls.offer = offer
