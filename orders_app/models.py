"""Models managing system purchases and execution status tracking."""

from django.conf import settings
from django.db import models
from offers_app.models import OfferDetails


class Order(models.Model):
    """Represents a finalized customer purchase instance from a specific tier package.

    Attributes:
        STATUS_CHOICES (list): Choice list defining legal state options for active tasks.
        offer_detail (ForeignKey): Reference to the purchased blueprint item configuration.
        customer_user (ForeignKey): Reference to the consumer who purchased the order.
        business_user (ForeignKey): Reference to the merchant responsible for executing the order.
        title (CharField): Snapshot title of the service package at checkout.
        revisions (PositiveIntegerField): Maximum allowed corrections allocated.
        delivery_time_in_days (PositiveIntegerField): Expected delivery countdown limit.
        price (DecimalField): Frozen financial snapshot total at payment timestamp.
        features (JSONField): Collection of features bundled into the contract tier.
        offer_type (CharField): Identifier indicating basic, standard, or premium tier types.
        status (CharField): State tracker monitoring execution progress.
        created_at (DateTimeField): Timestamp recording initial financial authorization.
        updated_at (DateTimeField): Timestamp recording latest structural state mutation.
    """

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

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

    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField(default=0)
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Returns string representation of the order containing identifier and customer name.

        Returns:
            str: Normalized descriptor tracking transactional identification strings.
        """
        return f"Order {self.id} - {self.title} (Customer: {self.customer_user.username})"
