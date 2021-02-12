from rest_framework import permissions

# from ..utils import can_modify_project

#
# class IsSuperuser(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return request.user.is_superuser
#
#
# class IsOceanUser(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return request.user.profile.oceanography
#
from travel.utils import can_modify_request


class CanModifyOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, "request_id"):
            return can_modify_request(request.user, obj.request_id)
        elif hasattr(obj, "traveller"):
            return can_modify_request(request.user, obj.traveller.request_id)
        else:
            return can_modify_request(request.user, obj.id)
