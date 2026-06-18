"""Serializers for the API app."""

from rest_framework import serializers


class BaseInfoSerializer(serializers.Serializer):
    """Serializer for system-wide aggregation metrics."""

    review_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    business_profile_count = serializers.IntegerField()
    offer_count = serializers.IntegerField()


"""Serializers for the API app."""


class BaseInfoSerializer(serializers.Serializer):
    """Serializer for system-wide aggregation metrics.

    Attributes:
        review_count (IntegerField): Total number of reviews across the platform.
        average_rating (FloatField): Cumulative average rating score of all businesses.
        business_profile_count (IntegerField): Total number of registered business profiles.
        offer_count (IntegerField): Total number of active offers available.
    """

    review_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    business_profile_count = serializers.IntegerField()
    offer_count = serializers.IntegerField()
