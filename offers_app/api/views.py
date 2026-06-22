"""ViewSets managing endpoint controllers and processing pipeline for offers."""

from rest_framework import viewsets, status, permissions as rf_permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from core.permissions import IsBusinessUser, IsOfferOwner
from django_filters.rest_framework import DjangoFilterBackend

from offers_app.models import Offers, OfferDetails
from offers_app.api.serializers import OfferReadSerializer, OfferWriteSerializer, OfferDetailsSerializer, OfferListSerializer
from offers_app.api.filters import OffersFilter


class StandardResultsSetPagination(PageNumberPagination):
    """Paginator specifying standardized query params and element maximum limits."""

    page_size = 6
    page_size_query_param = 'page_size'


class OfferViewSet(viewsets.ModelViewSet):
    """ViewSet processing CRUD endpoints and assigning rules for principal Offers."""

    queryset = Offers.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = OffersFilter
    search_fields = ['title', 'description']
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        """Selects serializer structure based on current safe/unsafe method action type."""
        if self.action == 'list':
            return OfferListSerializer
        elif self.action == 'retrieve':
            return OfferReadSerializer
        return OfferWriteSerializer

    def get_permissions(self):
        """Evaluates identity and applies strict role-based block exceptions to actions."""
        if self.action == 'list':
            return [rf_permissions.AllowAny()]
        elif self.action == 'retrieve':
            return [rf_permissions.IsAuthenticated()]
        elif self.action == 'create':
            return [rf_permissions.IsAuthenticated(), IsBusinessUser()]
        return [rf_permissions.IsAuthenticated(), IsOfferOwner()]

    def perform_create(self, serializer):
        """Executes save actions inside database context transaction frames."""
        serializer.save()

    def get_serializer_context(self):
        """Passes context dictionaries containing critical server state to serializers."""
        return {'request': self.request}

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests to ensure partial updates preserve existing data.

        This method explicitly sets partial=True to allow updating only provided fields
        and reloads the instance fresh from the database to ensure the response 
        contains all nested details, not just the updated ones.

        Args:
            request: The incoming HTTP request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response object containing the fully updated and serialized data.
        """
        kwargs['partial'] = True
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        fresh_instance = self.queryset.model.objects.get(pk=instance.pk)
        if hasattr(fresh_instance, '_prefetched_objects_cache'):
            fresh_instance._prefetched_objects_cache = {}

        fresh_serializer = self.get_serializer(fresh_instance)
        return Response(fresh_serializer.data)


class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet supplying read-only interaction limits to singular tier package entities."""

    queryset = OfferDetails.objects.all()
    serializer_class = OfferDetailsSerializer
    permission_classes = [rf_permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_context(self):
        """Augments tracking attributes across basic serializer configurations."""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
