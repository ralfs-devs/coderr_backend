"""Serializers handling user identity registrations, validation checks, and secure login verifications."""

from rest_framework import serializers
from user_auth_app.models import User
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer handling new account onboarding validations and password verification.

    Attributes:
        repeated_password (CharField): Write-only validation string used to cross-reference primary inputs.
    """

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        """Meta options configuration for RegistrationSerializer.

        Attributes:
            model (Model): Target database reference mapped to the authentication layer.
            fields (list): Exposed serialization properties transmitted through the payload interface.
            extra_kwargs (dict): Field modification flags handling input masking configuration properties.
        """

        model = User
        fields = ['username', 'email', 'type', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """Cross-checks consistency parameters between both provided password strings.

        Args:
            data (dict): Collection of unvalidated input mappings.

        Returns:
            dict: Evaluated data mapping structure cleared for ingestion.

        Raises:
            ValidationError: If the secondary validation string does not match the primary string.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})
        if data.get('type') not in ['customer', 'business']:
            raise serializers.ValidationError(
                {"type": "Type must be either 'customer' or 'business'"})
        return data

    def create(self, validated_data):
        """Discards redundancy attributes and registers a new secure instance in the system framework.

        Args:
            validated_data (dict): Sanitized payload properties verified by validation routines.

        Returns:
            User: Newly persisted instance built through standard hashing routines.
        """
        validated_data.pop('repeated_password')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Serializer handling login verification parameters and session authentication matching."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Verifies provided credentials against existing identity schemas.

        Args:
            data (dict): Plain text lookup credentials passed via connection headers.

        Returns:
            dict: The verified structural dataset matching active records.

        Raises:
            ValidationError: If the provided credential combination does not match an active user record.
        """
        user = authenticate(
            username=data['username'], password=data['password'])
        if user:
            self.user = user
            return data
        raise serializers.ValidationError("Invalid username or password.")
