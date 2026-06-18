"""Views providing controller logic and filter sets for processing customer orders."""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import viewsets, permissions as permits, status
from rest_framework.views import APIView
from rest_framework.response import Response

from orders_app.models import Order
from orders_app.api.serializers import OrderSerializer
from offers_app.models import OfferDetails
from core.permissions import IsCustomerUser, IsBusinessUser, IsStaff

User = get_user_model()


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet automating basic CRUD interactions and permission checks on orders.

    Attributes:
        serializer_class (Serializer): Default mapping framework used to transform data profiles.
        queryset (QuerySet): Base data statement querying system transactions.
    """

    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_permissions(self):
        """Deduces user role limitations based on requested action routines.

        Returns:
            list: Instantiated rule assertions validating access criteria.
        """
        if self.action in ['update', 'partial_update']:
            return [permits.IsAuthenticated(), IsBusinessUser()]

        if self.action == 'create':
            return [permits.IsAuthenticated(), IsCustomerUser()]

        if self.action == 'destroy':
            return [permits.IsAuthenticated(), IsStaff()]

        return [permits.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Creates an order instance using frozen parameter snapshots from specified details.

        Args:
            request (Request): Inbound client parameters package payload.
            *args (tuple): Positional parameter collection variables.
            **kwargs (dict): Custom tracking assignment components.

        Returns:
            Response: Entity snapshot mirroring the active persistence layer entry.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        offer_detail = get_object_or_404(
            OfferDetails, id=serializer.validated_data['offer_detail_id'])

        order = Order.objects.create(
            customer_user=request.user,
            business_user=offer_detail.offer.owner,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress'
        )

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        """Filters listings so users can exclusively fetch transactions they participate in.

        Returns:
            QuerySet: Structured collection tracking matching execution rows.
        """
        if self.action == 'list':
            return Order.objects.filter(
                Q(customer_user=self.request.user) | Q(
                    business_user=self.request.user)
            ).distinct()

        return Order.objects.all()


class OrderCountView(APIView):
    """Endpoint compiling count aggregates of active, processing orders."""

    def get(self, request, pk=None):
        """Evaluates ongoing contracts currently assigned to a distinct professional.

        Args:
            request (Request): The standard verification network resource package.
            pk (int): Target identifier for the business user being counted.

        Returns:
            Response: Metric wrapper housing calculated operational values.
        """
        get_object_or_404(User, pk=pk)
        count = Order.objects.filter(
            business_user_id=pk, status='in_progress').count()
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    """Endpoint calculating numerical aggregates of fully executed contracts."""

    def get(self, request, pk=None):
        """Counts historical instances successfully processed by a specific business owner.

        Args:
            request (Request): The standard verification network resource package.
            pk (int): Target identifier for the business user being counted.

        Returns:
            Response: Metric wrapper housing calculated operation summaries.
        """
        get_object_or_404(User, pk=pk)
        count = Order.objects.filter(
            business_user_id=pk, status='completed').count()
        return Response({'completed_order_count': count})
