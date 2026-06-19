"""Views providing controller configurations and context segmentation for user profiles."""

from rest_framework import viewsets, permissions as rf_permissions
from core.permissions import IsOwnerOrReadOnly
from profiles_app.models import Profile
from profiles_app.api.serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet managing endpoint controllers and layout abstractions for user profiles.

    Attributes:
        serializer_class (Serializer): Default translation map processing item layers.
        lookup_field (str): The database model field utilized for single resource lookups.
        permission_classes (list): Access validations required for interaction hooks.
    """

    serializer_class = ProfileSerializer
    lookup_field = 'pk'
    permission_classes = [rf_permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Filters the initial profile dataset based on structural route components.

        Returns:
            QuerySet: Filtered profile collection containing matching account type categories.
        """
        queryset = Profile.objects.all()

        path = self.request.path
        if 'business' in path:
            return queryset.filter(user__type='business')
        elif 'customer' in path:
            return queryset.filter(user__type='customer')

        return queryset

    def get_serializer_context(self):
        """Injects contextual route information to guide data rendering layers.

        Returns:
            dict: Meta variables mapping the current layout category to serializers.
        """
        context = super().get_serializer_context()

        path = self.request.path
        if 'business' in path:
            context['list_type'] = 'business'
        elif 'customer' in path:
            context['list_type'] = 'customer'
        else:
            context['list_type'] = 'detail'
        return context
