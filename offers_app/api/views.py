from rest_framework import viewsets, permissions as permits
from core.permissions import IsOwnerOrReadOnly, IsBusinessUser, IsOfferOwner
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Offers, OfferDetails
from .serializers import OfferReadSerializer, OfferWriteSerializer, OfferDetailsSerializer
from .filters import OffersFilter

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offers.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend]
    filterset_class = OffersFilter
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return OfferReadSerializer
        return OfferWriteSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permits.AllowAny()]
        elif self.action == 'retrieve':
            return [permits.IsAuthenticated()]
        elif self.action == 'create':
            return [permits.IsAuthenticated(), IsBusinessUser()]
        # Default für andere Aktionen (update, partial_update, destroy)
        return [permits.IsAuthenticated(), IsOfferOwner()]

    def perform_create(self, serializer):

        serializer.save()

    def get_serializer_context(self):
        return {'request': self.request}


class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfferDetails.objects.all()
    serializer_class = OfferDetailsSerializer
    permission_classes = [permits.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
