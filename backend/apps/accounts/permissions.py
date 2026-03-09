"""
Custom permissions for the accounts app.
"""

from rest_framework import permissions


class IsDealerUser(permissions.BasePermission):
    """Allow access only to users with the dealer role."""

    message = "Only dealers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "dealer"
        )


class IsBuyerUser(permissions.BasePermission):
    """Allow access only to users with the buyer role."""

    message = "Only buyers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "buyer"
        )


class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin users."""

    message = "Only administrators can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: allow write access only to the owner.

    For DealerProfile objects, the owner is the associated user.
    For other objects, expects an ``owner`` or ``user`` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # DealerProfile
        if hasattr(obj, "user"):
            return obj.user == request.user

        # Generic owner check
        if hasattr(obj, "owner"):
            return obj.owner == request.user

        return False


class IsVerifiedDealer(permissions.BasePermission):
    """Allow access only to dealers whose profile is verified."""

    message = "Only verified dealers can perform this action."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role != "dealer":
            return False
        try:
            return request.user.dealer_profile.is_verified
        except AttributeError:
            return False
