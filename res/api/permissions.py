from rest_framework import permissions

from .. import models
from ..utils import in_res_crud_group, can_modify_application


class CanModifyApplicationOrReadOnly(permissions.BasePermission):

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
            application_id = None
            # if this achievement belongs to this user...
            if isinstance(obj, models.Achievement) and obj.user == request.user:
                return True
            elif isinstance(obj, models.Application):
                application_id = obj.id
            elif isinstance(obj, models.ApplicationOutcome):
                application_id = obj.application.id

            return can_modify_application(request.user, application_id)


