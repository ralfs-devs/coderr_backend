from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Reviews(models.Model):

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

    def __str__(self):
        return f"Review {self.id} ({self.rating} Sterne)"
