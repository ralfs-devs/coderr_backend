"""Database models and query managers establishing customized database structures for core user accounts."""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    """Manager for the custom User model.

    Provides helper methods to create regular users and superusers.
    """

    def create_user(self, username, email, password, type=None, **extra_fields):
        """Creates and saves a User instance containing explicit security traits.

        Args:
            username (str): The distinct identifying string handle.
            email (str): The target mailbox address.
            password (str): The unhashed source credential string.
            type (str): The foundational operation profile classification.
            **extra_fields: Variable configuration mappings passed to schema instances.

        Returns:
            User: The freshly generated database entry instance.

        Raises:
            ValueError: When necessary lookup strings or handles are dropped.
        """

        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')

        email = self.normalize_email(email)

        user = self.model(username=username, email=email,
                          type=type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        """Creates and saves a superuser with the given details.

        Args:
            username (str): The unique username.
            email (str): The user's email address.
            password (str): The user's password.
            **extra_fields: Additional fields, defaults is_staff/is_superuser to True.

        Returns:
            User: The created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(username, email, password, type=None ** extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model extending AbstractBaseUser.

    Attributes:
        username (CharField): Unique identifier for the user.
        email (EmailField): Unique email address.
        type (CharField): Role of the user ('customer' or 'business').
        is_active (BooleanField): Determines if the user account is active.
        is_staff (BooleanField): Determines if the user has staff access.
    """

    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        """Returns the string representation of the user.

        Returns:
            str: The unique account identity identifier string.
        """
        return self.username
