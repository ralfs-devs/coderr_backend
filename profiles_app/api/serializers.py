"""Serializers handling profile data 
        transformations and nested user updates."""

from django.utils import timezone
from rest_framework import serializers
from profiles_app.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer managing profile instances and synchronous user model fields.

    Attributes:
        username (CharField): 
            Read-only account registration identifier.
        email (EmailField):
            Authoritative contact address synchronized from user storage.
        type (CharField):
            Read-only account configuration category profile tag.
    """

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')
    type = serializers.CharField(source='user.type', read_only=True)

    class Meta:
        """Meta options configuration for ProfileSerializer.

        Attributes:
            model (Model):
                Target model template mapped to the engine.
            fields (list):
                Collection of explicit database values parsed to interfaces.
            read_only_fields (list):
                Safeguarded model keys restricted from external modifications.
        """

        model = Profile
        fields = [
            'user',
            'username',
            'email',
            'type',
            'first_name',
            'last_name',
            'file',
            'uploaded_at',
            'location',
            'tel',
            'description',
            'working_hours',
            'created_at'
        ]
        read_only_fields = ['user', 'created_at']

    def to_representation(self, instance):
        """Normalizes null attributes and drops fields
                based on client query types.

        Args:
            instance (Profile):
                The database model entity currently being read.

        Returns:
            dict: Outbound JSON payload 
                structured according to profile configurations.
        """
        ret_val = super().to_representation(instance)
        for field in ['first_name',
                      'last_name', ''
                      'location',
                      'tel',
                      'description',
                      'working_hours']:
            if ret_val.get(field) is None:
                ret_val[field] = ""
        context_type = self.context.get('list_type')

        if context_type == 'customer':
            for field in ['location',
                          'tel',
                          'description',
                          'working_hours',
                          'created_at',
                          'email']:
                ret_val.pop(field, None)

        elif context_type == 'business':
            for field in ['uploaded_at', 'created_at', 'email']:
                ret_val.pop(field, None)
        return ret_val

    def update(self, instance, validated_data):
        """Handles deep updates for both 
            profile records and user email configurations.

        Args:
            instance (Profile): 
                The active persistence layer entry planned for mutation.
            validated_data (dict): 
                Cleaned input data verified by the field mappings.

        Returns:
            Profile: 
                The modified profile instance after committing changes.
        """
        user_data = validated_data.pop('user', {})
        email = validated_data.pop('email', user_data.get('email'))

        if email:
            instance.user.email = email
            instance.user.save()
        if 'file' in validated_data:
            instance.uploaded_at = timezone.now()

        return super().update(instance, validated_data)
