from rest_framework import permissions

from ..utils import is_crud_user


class herringCRUDOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        elif is_crud_user(request.user):
            return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        elif is_crud_user(request.user):
            return True
