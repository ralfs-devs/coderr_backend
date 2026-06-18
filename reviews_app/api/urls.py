"""
URL mapping for customer reviews concerning business-users.
"""

from django.urls import path
from .views import ReviewsViewSet

urlpatterns = [
    path('reviews/', ReviewsViewSet.as_view(actions={
         'get': 'list', 'post': 'create'}), name='reviews'),
    path('reviews/<int:pk>/', ReviewsViewSet.as_view(
        actions={'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='reviews-detail')
]
