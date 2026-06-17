from django.utils import timezone
from rest_framework import serializers
from ..models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')
    type = serializers.CharField(source='user.type', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'email', 'type', 'first_name', 'last_name',
            'file', 'uploaded_at', 'location', 'tel', 'description', 'working_hours', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']

    def to_representation(self, instance):
        ret_val = super().to_representation(instance)
        for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
            if ret_val.get(field) is None:
                ret_val[field] = ""
        context_type = self.context.get('list_type')

        if context_type == 'customer':
            for field in ['location', 'tel', 'description', 'working_hours', 'created_at', 'email']:
                ret_val.pop(field, None)

        elif context_type == 'business':
            for field in ['uploaded_at', 'created_at', 'email']:
                ret_val.pop(field, None)
        return ret_val

    def update(self, instance, validated_data):

        user_data = validated_data.pop('user', {})
        email = validated_data.pop('email', user_data.get('email'))

        if email:
            instance.user.email = email
            instance.user.save()
        if 'file' in validated_data:
            instance.uploaded_at = timezone.now()

        return super().update(instance, validated_data)
