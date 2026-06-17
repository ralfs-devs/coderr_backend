from rest_framework import serializers
from ..models import Reviews


class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ['id', 'business_user', 'reviewer', 'rating',
                  'description', 'created_at', 'updated_at']
        read_only_fields = ['reviewer', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError(
                "Rating must be between 1 and 5.")
        return value
