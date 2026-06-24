"""URL mapping for the profiles_app."""

from django.urls import path
from profiles_app.api.views import ProfileViewSet

urlpatterns = [
    path(
        'profiles/business/',
        ProfileViewSet.as_view({
            'get': 'list'
        }),
        name='business-profiles'
    ),
    path(
        'profiles/customer/',
        ProfileViewSet.as_view({
            'get': 'list'
        }),
        name='customer-profiles'
    ),
    path(
        'profile/<int:pk>/',
        ProfileViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update'
        }),
        name='profile-detail'
    )
]
