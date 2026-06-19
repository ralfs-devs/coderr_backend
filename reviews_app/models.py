"""Data Model for customer reviews concerning business-users."""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Reviews(models.Model):
    """Data model representing a customer review for a specific business profile.

    Attributes:
        business_user (ForeignKey): The business user profile being reviewed.
        reviewer (ForeignKey): The customer user profile creating the review.
        rating (IntegerField): The score given to the business, from 1 to 5.
        description (TextField): Optional text commentary provided by the reviewer.
        created_at (DateTimeField): Timestamp when the review was created.
        updated_at (DateTimeField): Timestamp when the review was last updated.
    """

    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_reviews'
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.TextField(null=True, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['business_user', 'reviewer'], name='unique_customer_review_per_business')
        ]
        verbose_name = 'Review'

    def __str__(self):
        """Generates a standard string representation of the review instance.

        Returns:
            str: A formatted string containing the review ID and rating score.
        """
        return f"Review {self.id} ({self.rating} Sterne)"
