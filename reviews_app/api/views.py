from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models import Reviews
from .serializers import ReviewsSerializer
from core.permissions import IsReviewOwner


class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsReviewOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):

        serializer.save(reviewer=self.request.user)

    def create(self, request, *args, **kwargs):

        try:
            return super().create(request, *args, **kwargs)
        except Exception:
            return Response(status=status.HTTP_403_FORBIDDEN)
