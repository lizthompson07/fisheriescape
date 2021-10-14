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
            request_id = None
            if isinstance(obj, models.Application):
                request_id = obj.id
            # elif isinstance(obj, models.CSASRequestReview) or isinstance(obj, models.CSASRequestNote):
            #     request_id = obj.csas_request.id
            return can_modify_application(request.user, request_id)


