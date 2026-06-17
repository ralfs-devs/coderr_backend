from rest_framework.reverse import reverse
from rest_framework import serializers
from ..models import Offers, OfferDetails


class OfferDetailsSerializer(serializers.ModelSerializer):
    # 'id' wird hier für das Update benötigt
    id = serializers.IntegerField(required=False)
    # URL wird für die Struktur benötigt
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetails
        fields = ['id', 'title', 'url', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type']

        # WICHTIG: Damit PATCH nicht bei fehlenden Feldern crasht:
        extra_kwargs = {
            'title': {'required': False},
            'revisions': {'required': False},
            'delivery_time_in_days': {'required': False},
            'price': {'required': False},
            'features': {'required': False},
            'offer_type': {'required': False},
        }

    def get_url(self, obj):
        return reverse('offers-detail', kwargs={'pk': obj.pk}, request=self.context.get('request'))


class OfferReadSerializer(serializers.ModelSerializer):
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(source='owner', read_only=True)

    class Meta:
        model = Offers
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_details(self, obj):
        request = self.context.get('request')
        return [
            {
                "id": d.id,
                "url": reverse('single-offer-details', kwargs={'pk': d.pk}, request=request)
            }
            for d in obj.details.all()
        ]

    def get_user_details(self, obj):
        profile = getattr(obj.owner, 'profile', None)
        return {
            'first_name': getattr(profile, 'first_name', ''),
            'last_name': getattr(profile, 'last_name', ''),
            'username': obj.owner.username
        }

    def get_min_price(self, obj):
        from django.db.models import Min
        return obj.details.aggregate(Min('price'))['price__min']

    def get_min_delivery_time(self, obj):
        from django.db.models import Min
        return obj.details.aggregate(Min('delivery_time_in_days'))['delivery_time_in_days__min']


class OfferWriteSerializer(serializers.ModelSerializer):
    details = OfferDetailsSerializer(many=True)

    class Meta:
        model = Offers
        fields = ['id', 'title', 'image', 'description', 'details']

    def create(self, validated_data):
        owner = self.context['request'].user
        details_data = validated_data.pop('details', [])
        offer = Offers.objects.create(owner=owner, **validated_data)
        for detail_data in details_data:
            OfferDetails.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
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
