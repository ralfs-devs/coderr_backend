"""Models representing core business offers and their respective tier details."""

from django.db import models
from django.conf import settings


class Offers(models.Model):
    """Represents a general service offer created by a business user.

    Attributes:
        owner (ForeignKey): Reference to the user who owns the offer.
        title (CharField): The headline or name of the service offer.
        description (TextField): Detailed explanation of what the offer covers.
        image (ImageField): Optional visual attachment representing the offer.
        created_at (DateTimeField): Timestamp when the offer was first created.
        updated_at (DateTimeField): Timestamp when the offer was last modified.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='offers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Returns the string representation of the offer.

        Returns:
            str: The title of the offer.
        """
        return self.title


class OfferDetails(models.Model):
    """Represents the tier-specific details (basic, standard, premium) of an offer.

    Attributes:
        TYPE_CHOICES (list): Choice list containing allowed service tier levels.
        offer (ForeignKey): Reference to the parent configuration offer instance.
        title (CharField): Specifically tailored title for the individual tier.
        revisions (PositiveIntegerField): Permitted correction loops for the customer.
        delivery_time_in_days (PositiveIntegerField): Planned execution timeline duration.
        price (DecimalField): Exact financial cost structure of the selected item.
        features (JSONField): Collection describing inclusions and custom traits.
        offer_type (CharField): Value tracking whether this represents a basic, standard, or premium tier.
    """

    TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    offer = models.ForeignKey(
        Offers,
        on_delete=models.CASCADE,
        related_name='details'
    )
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        """Returns the string representation combining offer title and type.

        Returns:
            str: Combined textual identification pattern for the specific object.
        """
        return f"{self.offer.title} - {self.offer_type}"
