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
        else:
            request_id = None
            if isinstance(obj, models.CSASRequest):
                request_id = obj.id
            elif isinstance(obj, models.CSASRequestReview):
                request_id = obj.csas_request.id
            return can_modify_request(request.user, request_id)


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
            elif isinstance(obj, models.Meeting) or isinstance(obj, models.Document) or isinstance(obj, models.ProcessNote):
                process_id = obj.process.id
            elif isinstance(obj, models.MeetingNote) or isinstance(obj, models.MeetingResource) or isinstance(obj, models.Invitee) or isinstance(obj, models.MeetingCost):
                process_id = obj.meeting.process.id
            elif isinstance(obj, models.DocumentNote) or isinstance(obj, models.DocumentCost) or isinstance(obj, models.Author) \
                    or isinstance(obj, models.DocumentTracking):
                process_id = obj.document.process.id
            return can_modify_process(request.user, process_id)
