"""
URL mapping for the offers_app.
"""

from django.urls import path

from offers_app.api.views import OfferDetailViewSet, OfferViewSet

urlpatterns = [
    path(
        'offers/',
        OfferViewSet.as_view({
            'get': 'list',
            'post': 'create'
        }),
        name='offers'
    ),
    path(
        'offers/<int:pk>/',
        OfferViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='offers-detail'
    ),
    path(
        'offerdetails/<int:pk>/',
        OfferDetailViewSet.as_view({
            'get': 'retrieve'
        }),
        name='single-offer-details'
    )
]
