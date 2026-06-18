"""Serializers for mapping Order model instances into structured API representations."""

from rest_framework import serializers
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializer handling creation payload inputs and read formatting for orders.

    Attributes:
        offer_detail_id (IntegerField): Write-only identification target linking blueprints.
    """

    offer_detail_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        """Meta options configuration for OrderSerializer.

        Attributes:
            model (Model): Target model template mapped to the engine.
            fields (list): Collection of explicit database values parsed to interfaces.
            read_only_fields (list): Safeguarded model keys restricted from external modifications.
        """

        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at', 'offer_detail_id'
        ]

        read_only_fields = [
            'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'created_at', 'updated_at'
        ]
