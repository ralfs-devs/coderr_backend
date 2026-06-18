"""Viewsets handling transactional evaluation workflows, permissions checks, and individual customer review operations."""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from reviews_app.models import Reviews
from reviews_app.api.serializers import ReviewsSerializer
from core.permissions import IsReviewOwner


class ReviewsViewSet(viewsets.ModelViewSet):
    """ModelViewSet managing public evaluation lists and protected individual review records.

    Attributes:
        queryset (QuerySet): Query representation mapping target records from the database layer.
        serializer_class (Serializer): Processing engine translating interfaces into internal records.
    """

    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer

    def get_permissions(self):
        """Instantiates and returns the list of permissions that this view requires.

        Returns:
            list: Instantiated permission rule objects evaluating target network contexts.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsReviewOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """Saves a new review instance, binding the requesting user profile as the static author.

        Args:
            serializer (Serializer): Validation instance hosting validated transfer payload structures.
        """
        serializer.save(reviewer=self.request.user)

    def create(self, request, *args, **kwargs):
        """Creates a review record instance while catching unique integrity drops and operational failures.

        Args:
            request (Request): Framework payload container hosting context and parameters.
            *args: Variable length argument modifier lists.
            **kwargs: Arbitrary key-value structural map extensions.

        Returns:
            Response: Framed network payload structure containing resource values or error flags.
        """
        try:
            return super().create(request, *args, **kwargs)
        except Exception:
            return Response(status=status.HTTP_403_FORBIDDEN)
