"""
URL mapping for the misc_app.
"""

from django.urls import path
from misc_app.api.views import BaseInfoView

urlpatterns = [
    path('base-info/',
         BaseInfoView.as_view(),
         name='base_info'
         )
]
