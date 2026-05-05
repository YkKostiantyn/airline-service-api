from rest_framework.permissions import BasePermission, SAFE_METHODS

class ReadOnlyOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        return (
            user
            and user.is_authenticated
            and getattr(user, "role", None) == "admin"
        )