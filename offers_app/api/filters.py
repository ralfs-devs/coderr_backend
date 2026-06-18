"""Filter sets for querying offers based on specific attribute ranges."""

from django_filters import rest_framework as filters
from offers_app.models import Offers


class OffersFilter(filters.FilterSet):
    """Filter class allowing filtering of offers by price and delivery time.

    Attributes:
        min_price (NumberFilter): Filter to match prices less than or equal to a value.
        max_delivery_time (NumberFilter): Filter to match delivery times less than or equal to a value.
    """

    min_price = filters.NumberFilter(field_name='min_price', lookup_expr='lte')
    max_delivery_time = filters.NumberFilter(
        field_name='delivery_time', lookup_expr='lte')

    class Meta:
        """Meta configuration for OffersFilter.

        Attributes:
            model (Model): The database model linked to this filter set.
            fields (list): The list of query fields available for filtering.
        """

        model = Offers
        fields = ['min_price', 'max_delivery_time']
