
from django.conf import settings
from django.db import models
from offers_app.models import OfferDetails


class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    # Referenz auf die Quelle (wichtig für Rückverfolgbarkeit)
    offer_detail = models.ForeignKey(
        OfferDetails,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    customer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='customer_orders'
    )

    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='business_orders'
    )

    # Snapshot-Felder (kopiert zum Zeitpunkt des Kaufs)
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField(default=0)
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10)

    # Status und Zeitstempel
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.title} (Customer: {self.customer_user.username})"
