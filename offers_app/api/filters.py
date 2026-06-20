"""Filter sets for querying offers based on specific attribute ranges."""

from django.db.models import Min
from django_filters import rest_framework as filters
from offers_app.models import Offers


class OffersFilter(filters.FilterSet):
    """Filter class allowing filtering of offers by price and delivery time."""

    creator_id = filters.NumberFilter(field_name='owner__id')
    min_price = filters.NumberFilter(method='filter_by_min_price')
    max_delivery_time = filters.NumberFilter(
        method='filter_by_max_delivery_time')

    class Meta:
        """Meta configuration for OffersFilter."""

        model = Offers
        fields = ['creator_id', 'min_price', 'max_delivery_time']

    def filter_by_min_price(self, queryset, name, value):
        """Filters offers ensuring the calculated lowest tier price is greater or equal.

        Args:
            queryset (QuerySet): The initial offers dataset.
            name (str): The filter field query key identifier.
            value (float): The pricing minimum boundary value.

        Returns:
            QuerySet: Filtered database query collection.
        """
        if value is None:
            return queryset
        return queryset.annotate(
            calculated_min_price=Min('details__price')
        ).filter(calculated_min_price__gte=value)

    def filter_by_max_delivery_time(self, queryset, name, value):
        """Filters offers ensuring the calculated shortest delivery time is less or equal.

        Args:
            queryset (QuerySet): The initial offers dataset.
            name (str): The filter field query key identifier.
            value (int): The delivery maximum full day limit.

        Returns:
            QuerySet: Filtered database query collection.
        """
        if value is None:
            return queryset
        return queryset.annotate(
            calculated_min_delivery=Min('details__delivery_time_in_days')
        ).filter(calculated_min_delivery__lte=value)
