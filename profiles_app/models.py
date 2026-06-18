"""Models managing extended user profiles and core synchronization triggers."""

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver


class Profile(models.Model):
    """Represents the extended profile information for a user.

    Attributes:
        user (OneToOneField): Link to the AUTH_USER_MODEL, acts as the primary key.
        first_name (CharField): The user's first name.
        last_name (CharField): The user's last name.
        file (ImageField): Path to the user's profile picture.
        uploaded_at (DateTimeField): Optional timestamp recording the latest asset update.
        location (CharField): The user's location.
        tel (CharField): The user's telephone number.
        description (TextField): A short biography or description.
        working_hours (CharField): The user's availability or working hours.
        created_at (DateTimeField): Automatically set timestamp when the profile is created.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile'
    )

    first_name = models.CharField(max_length=50, blank=True, default="")
    last_name = models.CharField(max_length=50, blank=True, default="")
    file = models.ImageField(upload_to='profiles/', blank=True, null=True)
    uploaded_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, default="")
    tel = models.CharField(max_length=20, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=50, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        """Returns the string representation of the profile.

        Returns:
            str: Normalized identification name referencing the core user record.
        """
        return f"Profile for {self.user.username}"


User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Creates a Profile instance automatically when a new User is created.

    Args:
        sender (Model): The model class that sent the signal.
        instance (User): The actual instance being saved.
        created (bool): True if a new record was created.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Saves the associated Profile instance when the User is saved.

    Args:
        sender (Model): The model class that sent the signal.
        instance (User): The actual instance being saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
