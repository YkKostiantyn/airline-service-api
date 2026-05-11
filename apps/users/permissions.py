from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import UserRole

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == UserRole.ADMIN
        )

class IsSelfOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        if getattr(user, "role", None) == UserRole.ADMIN:
            return True

        return obj == user