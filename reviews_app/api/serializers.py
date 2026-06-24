"""Serializers handling evaluation records and scoring inputs 
    for business profiles."""

from rest_framework import serializers
from reviews_app.models import Reviews


class ReviewsSerializer(serializers.ModelSerializer):
    """Serializer managing reviews instances and data constraints.

    Attributes:
        model (Model): 
            Target model template mapped to the engine.
        fields (list): 
            Collection of explicit database values parsed to interfaces.
        read_only_fields (list): 
            Safeguarded model keys restricted from external modifications.
    """

    class Meta:
        """Meta options configuration for ReviewsSerializer."""

        model = Reviews
        fields = ['id', 'business_user', 'reviewer', 'rating',
                  'description', 'created_at', 'updated_at']
        read_only_fields = ['reviewer', 'created_at', 'updated_at']

    def validate_rating(self, value):
        """Validates that the provided rating score 
            stays within the permitted scale limits.

        Args:
            value (int):
                The numeric rating score value to be verified.

        Returns:
            int: 
                The verified numeric score value.

        Raises:
            ValidationError: 
                If the rating score falls outside the range of 1 to 5.
        """
        if not (1 <= value <= 5):
            raise serializers.ValidationError(
                "Rating must be between 1 and 5.")
        return value
