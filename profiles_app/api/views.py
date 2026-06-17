from rest_framework import viewsets, permissions as permits
from core.permissions import IsOwnerOrReadOnly
from ..models import Profile
from .serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):

    serializer_class = ProfileSerializer
    lookup_field = 'pk'
    permission_classes = [permits.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Profile.objects.all()

        path = self.request.path
        if 'business' in path:
            return queryset.filter(user__type='business')
        elif 'customer' in path:
            return queryset.filter(user__type='customer')

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()

        path = self.request.path
        if 'business' in path:
            context['list_type'] = 'business'
        elif 'customer' in path:
            context['list_type'] = 'customer'
        else:
            context['list_type'] = 'detail'
        return context
