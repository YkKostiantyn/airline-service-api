from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import UserRole

class IsTicketOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        if getattr(user, "role", None) == UserRole.ADMIN:
            return True

        if request.method in SAFE_METHODS:
            return obj.order is None or obj.order.user == user

        return False