from django.contrib import admin
from offers_app.models import Offers, OfferDetails


@admin.register(Offers)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for Offers instances."""

    list_display = ("owner", "title", "description",
                    "image", "created_at", "updated_at")


@admin.register(OfferDetails)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for OfferDetails instances."""

    list_display = ("id", "offer", "title", "revisions",
                    "delivery_time_in_days", "price", "features", "offer_type")
