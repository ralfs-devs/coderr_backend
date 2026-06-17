"""
URL Configuration for Profile Management.

This module defines the URL patterns for handling business and customer profile
requests. It maps specific URL routes to their corresponding class-based views
(:inlineEntity{type="inline_entity" conversation="092b246a954d9e84f41e899ea51aa09cd7c8" name="ProfileListView"} and :inlineEntity{type="inline_entity" conversation="092b246a954d9e84f41e899ea51aa09cd7c8" name="ProfileDetailView"}).

URL Patterns:
    - profiles/business/: Lists all business profiles.
    - profiles/customer/: Lists all customer profiles.
    - profiles/<int:pk>/: Retrieves details for a specific profile by primary key.
"""

from django.urls import path
from .views import ProfileViewSet

urlpatterns = [
    path('profiles/business/',
         ProfileViewSet.as_view(actions={'get': 'list'}), name='business-profiles'),
    path('profiles/customer/',
         ProfileViewSet.as_view(actions={'get': 'list'}), name='customer-profiles'),
    path('profile/<int:pk>/', ProfileViewSet.as_view(
        actions={'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='profile-detail'),
]
