"""API endpoints handling incoming network requests
    for user account creation and validation sessions."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from user_auth_app.api.serializers import (RegistrationSerializer,
                                           LoginSerializer)


class RegistrationView(APIView):
    """Endpoint for onboarding new system users 
        and establishing authentic session keys."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Processes payload properties 
            to generate a distinct user entity and issues an API token.

        Args:
            request (Request): 
                Framework context vehicle carrying account data values.

        Returns:
            Response: 
                Framed network payload mapping core profile fields 
                    and the authorization key.
        """
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.pk
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Endpoint verifying network connection keys 
        against identity stores to unlock session paths."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validates provided lookup properties 
            to authenticate records and return active access keys.

        Args:
            request (Request): 
                Framework context vehicle containing profile tracking strings.

        Returns:
            Response: 
                Framed network payload reflecting core account metrics 
                    and session signatures.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.user
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.pk
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
