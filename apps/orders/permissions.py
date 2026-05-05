from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOrderOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if getattr(user, "role", None) == "admin":
            return True
        if request.method in SAFE_METHODS:
            return obj.user == user

        return False