from rest_framework import permissions
from rest_framework.generics import get_object_or_404

from ..utils import in_scuba_crud_group
from .. import models



class ScubaCRUDOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        elif in_scuba_crud_group(request.user):
            return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        elif in_scuba_crud_group(request.user):
            return True


