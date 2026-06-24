"""URL mapping for customer reviews concerning business-users."""

from django.urls import path
from reviews_app.api.views import ReviewsViewSet

urlpatterns = [
    path(
        'reviews/',
        ReviewsViewSet.as_view({
            'get': 'list',
            'post': 'create'
        }),
        name='reviews'
    ),
    path(
        'reviews/<int:pk>/',
        ReviewsViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='reviews-detail'
    )
]
