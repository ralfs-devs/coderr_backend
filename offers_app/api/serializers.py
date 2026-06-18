"""Serializers for the offers application API endpoints."""

from rest_framework.reverse import reverse
from rest_framework import serializers
from offers_app.models import Offers, OfferDetails


class OfferDetailsSerializer(serializers.ModelSerializer):
    """Serializer for nested offer details and tier options."""

    id = serializers.IntegerField(required=False)
    url = serializers.SerializerMethodField()

    class Meta:
        """Meta options for OfferDetailsSerializer."""

        model = OfferDetails
        fields = ['id', 'title', 'url', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type']
        extra_kwargs = {
            'title': {'required': False},
            'revisions': {'required': False},
            'delivery_time_in_days': {'required': False},
            'price': {'required': False},
            'features': {'required': False},
            'offer_type': {'required': False},
        }

    def get_url(self, obj):
        """Generates the absolute URL for the specific offer details tier instance.

        Args:
            obj (OfferDetails): The current offer details object instance.

        Returns:
            str: The fully qualified URL string pointing to the details resource.
        """
        return reverse('offers-detail', kwargs={'pk': obj.pk}, request=self.context.get('request'))


class OfferReadSerializer(serializers.ModelSerializer):
    """Serializer optimized for retrieving and displaying complex offer structures."""

    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(source='owner', read_only=True)

    class Meta:
        """Meta options for OfferReadSerializer."""

        model = Offers
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_details(self, obj):
        """Compiles minimal identifier and unique routing resource links for related tiers.

        Args:
            obj (Offers): The parent offer instance being processed.

        Returns:
            list[dict]: A list containing the target database id and target routing string.
        """
        request = self.context.get('request')
        return [
            {
                "id": d.id,
                "url": reverse('single-offer-details', kwargs={'pk': d.pk}, request=request)
            }
            for d in obj.details.all()
        ]

    def get_user_details(self, obj):
        """Resolves connected ownership records to pull foundational user metadata.

        Args:
            obj (Offers): The parent offer instance containing the owner reference.

        Returns:
            dict: Structured dataset defining names and system identification keys.
        """
        profile = getattr(obj.owner, 'profile', None)
        return {
            'first_name': getattr(profile, 'first_name', ''),
            'last_name': getattr(profile, 'last_name', ''),
            'username': obj.owner.username
        }

    def get_min_price(self, obj):
        """Calculates the lowest price value across all related offer tiers.

        Args:
            obj (Offers): The parent offer instance being processed.

        Returns:
            Decimal or None: The lowest recorded pricing figure for sub-elements.
        """
        from django.db.models import Min
        return obj.details.aggregate(Min('price'))['price__min']

    def get_min_delivery_time(self, obj):
        """Determines the shortest delivery timeline variant from associated sets.

        Args:
            obj (Offers): The parent offer instance being processed.

        Returns:
            int or None: Smallest entry tracking duration in full days.
        """
        from django.db.models import Min
        return obj.details.aggregate(Min('delivery_time_in_days'))['delivery_time_in_days__min']


class OfferWriteSerializer(serializers.ModelSerializer):
    """Serializer designed to process and validate inbound modifications or creation payloads."""

    details = OfferDetailsSerializer(many=True)

    class Meta:
        """Meta options for OfferWriteSerializer."""

        model = Offers
        fields = ['id', 'title', 'image', 'description', 'details']

    def create(self, validated_data):
        """Saves parent core parameters and creates dependent data collections.

        Args:
            validated_data (dict): Cleaned input values extracted from requests.

        Returns:
            Offers: The newly constructed persistence instances.
        """
        owner = self.context['request'].user
        details_data = validated_data.pop('details', [])
        offer = Offers.objects.create(owner=owner, **validated_data)
        for detail_data in details_data:
            OfferDetails.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        """Applies configuration updates on parent values while tracking sub-tier mutations.

        Args:
            instance (Offers): Original target asset record state.
            validated_data (dict): Replacement parameter keys and data clusters.

        Returns:
            Offers: The fully adjusted modified target model instances.
        """
        details_data = validated_data.pop('details', None)
        instance = super().update(instance, validated_data)
        if details_data is not None:
            for detail_data in details_data:
                detail_id = detail_data.get('id')
                if detail_id:
                    detail = OfferDetails.objects.get(
                        id=detail_id, offer=instance)
                    for attr, value in detail_data.items():
                        setattr(detail, attr, value)
                    detail.save()
                else:
                    OfferDetails.objects.create(offer=instance, **detail_data)
        return instance
