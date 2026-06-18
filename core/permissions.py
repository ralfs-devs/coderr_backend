"""Global Permissions for the API.

All Custom permissions are defined here.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission to only allow owners of an object to edit it.

    Otherwise only read operations are allowed.
    """

    def has_object_permission(self, request, view, obj):
        """Checks if the requesting user is the owner of the object for write operations.

        Args:
            request (Request): The HTTP request object.
            view (View): The view instance handling the request.
            obj (Model): The object instance being accessed.

        Returns:
            bool: True if the request method is safe or the user is the owner, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsBusinessUser(permissions.BasePermission):
    """Access granted for "business" user only."""

    def has_permission(self, request, view):
        """Checks global permission based on the user's type.

        Args:
            request (Request): The HTTP request object.
            view (View): The view instance handling the request.

        Returns:
            bool: True if the user is authenticated and has the type 'business', False otherwise.
        """
        if not request.user.is_authenticated:
            return False

        from django.contrib.auth import get_user_model
        User = get_user_model()
        fresh_user = User.objects.get(pk=request.user.pk)

        return fresh_user.type == 'business'

    def has_object_permission(self, request, view, obj):
        """Checks object-level permission for a business user.

        Args:
            request (Request): The HTTP request object.
            view (View): The view instance handling the request.
            obj (Model): The object instance being accessed.

        Returns:
            bool: True if the object's business_user_id matches the requesting user's ID, False otherwise.
        """
        return obj.business_user_id == request.user.id


class IsCustomerUser(permissions.BasePermission):
    """Access granted for "customer" users only."""

    def has_permission(self, request, view):
        """Checks if the user is authenticated and is a customer.

        Args:
            request (Request): The HTTP request object.
            view (View): The view instance handling the request.

        Returns:
            bool: True if authenticated and type is 'customer', False otherwise.
        """
        return (
            request.user.is_authenticated and getattr(
                request.user, 'type', None) == 'customer'
        )

    def has_object_permission(self, request, view, obj):
        """Checks if the authenticated customer owns the specific object.

        Args:
            request (Request): The HTTP request object.
            view (View): The view instance handling the request.
            obj (Model): The object instance being accessed.

        Returns:
            bool: True if the object's owner matches the requesting user, False otherwise.
        """
        return (obj.owner == request.user)


class IsOfferOwner(permissions.BasePermission):
    """Access granted for the owner of the offer only."""

    def has_permission(self, request, view):
        """Checks if the user is authenticated and a business entity.

        Args:
            request (Request): The HTTP request object.
            view (View): The view instance handling the request.

        Returns:
            bool: True if authenticated and type is 'business', False otherwise.
        """
        return (
            request.user.is_authenticated and getattr(
                request.user, 'type', None) == 'business'
        )

    def has_object_permission(self, request, view, obj):
        """Checks if the user is the specific owner of the offer.

        Args:
            request (Request): The HTTP request object.
            view (View): The view instance handling the request.
            obj (Model): The object instance being accessed.

        Returns:
            bool: True if the object's owner matches the requesting user, False otherwise.
        """
        return (obj.owner == request.user)


class IsStaff(permissions.BasePermission):
    """Access granted for staff users only."""

    def has_permission(self, request, view):
        """Checks if the user belongs to the Django staff group.

        Args:
            request (Request): The HTTP request object.
            view (View): The view instance handling the request.

        Returns:
            bool: True if the user is a staff member, False otherwise.
        """
        return bool(request.user and request.user.is_staff)


class IsReviewOwner(permissions.BasePermission):
    """Access granted to the author of the review only."""

    def has_object_permission(self, request, view, obj):
        """Checks if the requesting user created the review.

        Args:
            request (Request): The HTTP request object.
            view (View): The view instance handling the request.
            obj (Model): The object instance being accessed.

        Returns:
            bool: True if the object's reviewer matches the requesting user, False otherwise.
        """
        return obj.reviewer == request.user
