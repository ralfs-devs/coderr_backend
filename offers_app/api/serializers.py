from rest_framework import serializers
from rest_framework.reverse import reverse
from offers_app.models import Offers, OfferDetails


class OfferDetailsSerializer(serializers.ModelSerializer):
    """Serializer designed for full read/write operations on individual offer detail tiers."""

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
        required=False
    )

    class Meta:
        """Meta options for OfferDetailsSerializer."""

        model = OfferDetails
        fields = ['id', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type']
        extra_kwargs = {
            'title': {'required': False},
            'revisions': {'required': False},
            'delivery_time_in_days': {'required': False},
            'features': {'required': False},
            'offer_type': {'required': True},
        }


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
            list[dict]: A list containing strictly the target database id and absolute routing string.
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
            int or None: The lowest recorded pricing figure for sub-elements.
        """
        from django.db.models import Min
        price = obj.details.aggregate(Min('price'))['price__min']
        return int(price) if price is not None else None

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
        """Compiles relative routing resource links for related tiers.

        Args:
            obj (Offers): The parent offer instance being processed.

        Returns:
            list[dict]: A list containing strictly the target database id and relative routing string.
        """
        return [
            {
                "id": d.id,
                "url": f"/offerdetails/{d.id}/"
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


class OfferWriteSerializer(serializers.ModelSerializer):
    """Serializer designed to process and validate inbound modifications or creation payloads."""

    details = serializers.JSONField(required=False)

    class Meta:
        """Meta options for OfferWriteSerializer."""

        model = Offers
        fields = ['id', 'title', 'image', 'description', 'details']

    def to_representation(self, instance):
        """Formats the output representation containing all fields and all 3 updated/original details."""
        representation = super().to_representation(instance)

        db_details = OfferDetails.objects.filter(
            offer_id=instance.id
        ).order_by('id')

        representation['details'] = [
            {
                "id": d.id,
                "title": d.title,
                "revisions": d.revisions,
                "delivery_time_in_days": d.delivery_time_in_days,
                "price": float(d.price) if d.price is not None else 0.0,
                "features": d.features,
                "offer_type": d.offer_type
            }
            for d in db_details
        ]

        return representation

    def validate_details(self, value):
        """Validates that the details array contains exactly the three required package tiers."""
        if value is None:
            return value

        if not isinstance(value, list):
            raise serializers.ValidationError("Details must be a list.")

        request = self.context.get('request')
        is_partial = request and request.method == 'PATCH'

        if is_partial:
            return value

        required_types = {'basic', 'standard', 'premium'}
        provided_types = [item.get('offer_type')
                          for item in value if isinstance(item, dict)]

        if set(provided_types) != required_types or len(provided_types) != 3:
            raise serializers.ValidationError(
                "An offer must contain exactly three detail packages: basic, standard, and premium."
            )

        return value

    def create(self, validated_data):
        """Saves parent core parameters and creates dependent data collections."""
        owner = self.context['request'].user
        details_data = validated_data.pop('details', [])
        offer = Offers.objects.create(owner=owner, **validated_data)
        for detail_data in details_data:
            OfferDetails.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        """Updates specified fields and merges patched details into existing tiers without touching others."""
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        details_data = validated_data.get('details')

        if details_data:
            incoming_details_map = {
                item['offer_type']: item for item in details_data if 'offer_type' in item
            }
            existing_details = OfferDetails.objects.filter(
                offer_id=instance.pk)

            for detail in existing_details:
                if detail.offer_type in incoming_details_map:
                    data = incoming_details_map[detail.offer_type]
                    detail.title = data.get('title', detail.title)
                    detail.revisions = data.get('revisions', detail.revisions)
                    detail.delivery_time_in_days = data.get(
                        'delivery_time_in_days', detail.delivery_time_in_days)
                    detail.price = data.get('price', detail.price)
                    detail.features = data.get('features', detail.features)
                    detail.save()

        return instance
