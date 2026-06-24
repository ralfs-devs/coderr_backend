"""URL Configuration for User Authentication.

This module defines the URL patterns for handling user registration 
and login requests. 
It maps specific URL routes to their corresponding class-based views

URL Patterns:
    - registration/: Allows users to register.
    - login/: Allows users to log in.
"""

from django.urls import path
from user_auth_app.api.views import LoginView, RegistrationView

urlpatterns = [
    path(
        'registration/',
        RegistrationView.as_view(),
        name='user_registration'
    ),
    path(
        'login/',
        LoginView.as_view(),
        name='user_login'
    )
]
