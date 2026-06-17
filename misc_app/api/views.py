from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.db.models import Avg, Count
from django.contrib.auth import get_user_model

from offers_app.models import Offers
from reviews_app.models import Reviews
from .serializers import BaseInfoSerializer

User = get_user_model()


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):

        review_stats = Reviews.objects.aggregate(
            count=Count('id'),
            avg=Avg('rating')
        )

        data = {
            'review_count': review_stats['count'] or 0,
            'average_rating': float(review_stats['avg'] or 0.0),
            'business_profile_count': User.objects.filter(type='business').count(),
            'offer_count': Offers.objects.count()
        }

        serializer = BaseInfoSerializer(data)
        return Response(serializer.data)
