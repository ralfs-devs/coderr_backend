from django.contrib import admin
from profiles_app.models import Profile


@admin.register(Profile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile instances."""

    list_display = ("user", "first_name", "last_name", "file",
                    "location", "tel", "description", "working_hours", "created_at")
