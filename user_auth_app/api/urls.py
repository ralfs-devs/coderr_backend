"""URL Configuration for User Authentication.

This module defines the URL patterns for handling user registration and login requests. 
It maps specific URL routes to their corresponding class-based views

URL Patterns:
    - register/: Allows users to register.
    - login/: Allows users to log in.
"""

from django.urls import path
from .views import RegistrationView, LoginView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='user_registration'),
    path('login/', LoginView.as_view(), name='user_login'),
]
