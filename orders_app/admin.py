from django.contrib import admin
from orders_app.models import Order


@admin.register(Order)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile instances."""

    list_display = ("id", "offer_detail", "customer_user", "business_user", "title", "revisions",
                    "delivery_time_in_days", "price", "features", "offer_type", "status", "created_at", "updated_at")
