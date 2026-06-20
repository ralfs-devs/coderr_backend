

from rest_framework import serializers
from rest_framework.reverse import reverse
from offers_app.models import Offers, OfferDetails


class OfferDetailsSerializer(serializers.ModelSerializer):
    """Serializer for nested offer details and tier options."""

    id = serializers.IntegerField(required=False)
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False, required=False)

    class Meta:
        """Meta options for OfferDetailsSerializer."""

        model = OfferDetails
        fields = ['id', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type']
        extra_kwargs = {
            'title': {'required': False},
            'revisions': {'required': False},
            'delivery_time_in_days': {'required': False},
            'price': {'required': False},
            'features': {'required': False},
            'offer_type': {'required': False},
        }

    def to_internal_value(self, data):
        """Injects the existing record ID based on the offer_type mapping.

        Args:
            data (dict): The unvalidated incoming primitive data dictionary.

        Returns:
            dict: The validated and structurally augmented internal data dataset.
        """
        if not data.get('id'):
            offer_serializer = self.parent.parent if self.parent else None
            if offer_serializer and offer_serializer.instance:
                otype = data.get('offer_type')
                if otype:
                    existing_detail = offer_serializer.instance.details.filter(
                        offer_type=otype).first()
                    if existing_detail:
                        data['id'] = existing_detail.id
        return super().to_internal_value(data)

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
    details = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(source='owner', read_only=True)

    class Meta:
        """Meta options for OfferReadSerializer."""

        model = Offers
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time'
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


class OfferListSerializer(OfferReadSerializer):
    """Serializer explicitly designed for the strict paginated list view requirements."""

    user_details = serializers.SerializerMethodField()

    class Meta(OfferReadSerializer.Meta):
        """Meta options extending the base read serializer fields."""

        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_details(self, obj):
        """Overridden to exclude the URL from details list as required by the list specification.

        Args:
            obj (Offers): The parent offer instance being processed.

        Returns:
            list[dict]: A list containing only the target database id.
        """
        return [{"id": d.id} for d in obj.details.all()]

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


class OfferWriteSerializer(serializers.ModelSerializer):
    """Serializer designed to process and validate inbound modifications or creation payloads."""

    details = OfferDetailsSerializer(many=True, read_only=True)

    class Meta:
        """Meta options for OfferWriteSerializer."""

        model = Offers
        fields = ['id', 'title', 'image', 'description', 'details']

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
                "title": d.title,
                "revisions": d.revisions,
                "delivery_time_in_days": d.delivery_time_in_days,
                "price": d.price,
                "features": d.features,
                "offer_type": d.offer_type,
                "url": reverse('single-offer-details', kwargs={'pk': d.pk}, request=request) if request else ''
            }
            for d in obj.details.all().order_by('id')
        ]

    def create(self, validated_data):
        """Saves parent core parameters and creates dependent data collections.

        Args:
            validated_data (dict): Cleaned input values extracted from requests.

        Returns:
            Offers: The newly constructed persistence instances.
        """
        owner = self.context['request'].user
        details_data = self.initial_data.get('details', [])
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
        instance = super().update(instance, validated_data)
        details_data = self.initial_data.get('details', None)

        if details_data is not None:
            for detail_item in details_data:
                otype = detail_item.get('offer_type')
                if otype:
                    try:
                        detail = instance.details.get(offer_type=otype)
                        for attr, value in detail_item.items():
                            setattr(detail, attr, value)
                        detail.save()
                    except instance.details.model.DoesNotExist:
                        pass

            if hasattr(instance, '_prefetched_objects_cache'):
                instance._prefetched_objects_cache.clear()
            if hasattr(instance, '_details_cache'):
                delattr(instance, '_details_cache')

        return instance
