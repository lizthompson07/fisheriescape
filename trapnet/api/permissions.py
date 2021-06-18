from rest_framework import permissions
from rest_framework.generics import get_object_or_404

from ..utils import is_admin
from .. import models



class TrapnetCRUDOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        elif is_admin(request.user):
            return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        elif is_admin(request.user):
            return True


