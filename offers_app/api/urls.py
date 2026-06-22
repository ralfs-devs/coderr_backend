"""
URL mapping for the offers_app.
"""

from django.urls import path
from .views import OfferViewSet, OfferDetailViewSet

urlpatterns = [
    path('offers/', OfferViewSet.as_view(actions={
         'get': 'list', 'post': 'create'}), name='offers'),
    path('offers/<int:pk>/', OfferViewSet.as_view(actions={'get': 'retrieve',
         'patch': 'partial_update', 'delete': 'destroy'}), name='offers-detail'),
    path('offerdetails/<int:pk>/',
         OfferDetailViewSet.as_view(actions={'get': 'retrieve'}), name='single-offer-details')
]
