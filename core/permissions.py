"""
Global Permissions for the API.
All Custom permissions are defined here.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow owners of an object to edit it.
    Elswise only read operations are allowed.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsBusinessUser(permissions.BasePermission):
    """
    Access granted for "business" user only.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        from django.contrib.auth import get_user_model
        User = get_user_model()
        fresh_user = User.objects.get(pk=request.user.pk)

        return fresh_user.type == 'business'

    def has_object_permission(self, request, view, obj):

        return obj.business_user_id == request.user.id


class IsCustomerUser(permissions.BasePermission):
    """
    Access granted for "customer"- users only.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and getattr(
                request.user, 'type', None) == 'customer'
        )

    def has_object_permission(self, request, view, obj):
        return (obj.owner == request.user)


class IsOfferOwner(permissions.BasePermission):
    """
    Access granted for the owner of the offer only.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and getattr(
                request.user, 'type', None) == 'business'
        )

    def has_object_permission(self, request, view, obj):

        return (obj.owner == request.user)


class IsStaff(permissions.BasePermission):
    """
    Access granted for staff users only.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsReviewOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # PATCH/DELETE: Nur der Ersteller darf
        return obj.reviewer == request.user
