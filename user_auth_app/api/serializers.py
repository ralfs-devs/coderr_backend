from rest_framework import serializers
from ..models import User
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data['username'], password=data['password'])
        if user:
            self.user = user
            return data
        raise serializers.ValidationError("Invalid username or password.")
