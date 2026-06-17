from django_filters import rest_framework as filters
from ..models import Offers


class OffersFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name='min_price', lookup_expr='lte')
    max_delivery_time = filters.NumberFilter(
        field_name='delivery_time', lookup_expr='lte')

    class Meta:
        model = Offers
        fields = ['min_price', 'max_delivery_time']
