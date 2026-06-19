from django.contrib import admin
from reviews_app.models import Reviews


@admin.register(Reviews)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for Reviews model."""

    list_display = ("id", "business_user", "reviewer", "rating",
                    "description", "created_at", "updated_at")
