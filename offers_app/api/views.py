"""ViewSets managing endpoint controllers and processing pipeline for offers."""

from rest_framework import viewsets, permissions as permits
from core.permissions import IsBusinessUser, IsOfferOwner
from django_filters.rest_framework import DjangoFilterBackend

from offers_app.models import Offers, OfferDetails
from offers_app.api.serializers import OfferReadSerializer, OfferWriteSerializer, OfferDetailsSerializer
from offers_app.api.filters import OffersFilter

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Paginator specifying standardized query params and element maximum limits."""

    page_size = 6
    page_size_query_param = 'page_size'


class OfferViewSet(viewsets.ModelViewSet):
    """ViewSet processing CRUD endpoints and assigning rules for principal Offers."""

    queryset = Offers.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend]
    filterset_class = OffersFilter
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        """Selects serializer structure based on current safe/unsafe method action type."""
        if self.action in ['list', 'retrieve']:
            return OfferReadSerializer
        return OfferWriteSerializer

    def get_permissions(self):
        """Evaluates identity and applies strict role-based block exceptions to actions."""
        if self.action == 'list':
            return [permits.AllowAny()]
        elif self.action == 'retrieve':
            return [permits.IsAuthenticated()]
        elif self.action == 'create':
            return [permits.IsAuthenticated(), IsBusinessUser()]
        return [permits.IsAuthenticated(), IsOfferOwner()]

    def perform_create(self, serializer):
        """Executes save actions inside database context transaction frames."""
        serializer.save()

    def get_serializer_context(self):
        """Passes context dictionaries containing critical server state to serializers."""
        return {'request': self.request}


class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet supplying read-only interaction limits to singular tier package entities."""

    queryset = OfferDetails.objects.all()
    serializer_class = OfferDetailsSerializer
    permission_classes = [permits.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_context(self):
        """Augments tracking attributes across basic serializer configurations."""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
