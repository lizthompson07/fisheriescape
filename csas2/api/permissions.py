from rest_framework import permissions

from ..utils import can_modify_request


class CanModifyOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        elif can_modify_request(request.user, obj.id):
            return True
