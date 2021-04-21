from rest_framework import permissions

from .. import models
from ..utils import can_modify_request, can_modify_process


class CanModifyRequestOrReadOnly(permissions.BasePermission):

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


class CanModifyProcessOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            process_id = None
            if isinstance(obj, models.Process):
                process_id = obj.id
            elif isinstance(obj, models.Meeting) or isinstance(obj, models.Document):
                process_id = obj.process.id
            return can_modify_process(request.user, process_id)
