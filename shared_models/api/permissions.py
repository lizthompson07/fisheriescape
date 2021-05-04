from rest_framework import permissions

from shared_models.views import in_admin_group


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        elif in_admin_group(request.user):
            return True
