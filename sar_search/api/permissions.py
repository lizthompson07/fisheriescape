from rest_framework import permissions
from rest_framework.generics import get_object_or_404

from .. import models

class CanReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return True




