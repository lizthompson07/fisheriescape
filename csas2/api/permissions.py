from rest_framework import permissions

from .. import models
from ..utils import can_modify_request, can_modify_process, can_modify_request_review, can_modify_tor


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
            elif isinstance(obj, models.CSASRequestReview) or isinstance(obj, models.CSASRequestNote):
                request_id = obj.csas_request.id
            return can_modify_request(request.user, request_id)


class CanModifyRequestReviewOrReadOnly(permissions.BasePermission):

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
            request_id = obj.csas_request.id
            return can_modify_request_review(request.user, request_id)


class RequestNotesPermission(permissions.BasePermission):

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
            elif isinstance(obj, models.CSASRequestReview) or isinstance(obj, models.CSASRequestNote):
                request_id = obj.csas_request.id
            if can_modify_request(request.user, request_id):
                return True
            # if someone is modifying something they created, they can
            if request.user == obj.created_by:
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
            elif isinstance(obj, models.Meeting) or isinstance(obj, models.Document) or isinstance(obj, models.ProcessNote) or \
                    isinstance(obj, models.ProcessCost) or isinstance(obj, models.TermsOfReference):
                process_id = obj.process.id
            elif isinstance(obj, models.MeetingNote) or isinstance(obj, models.MeetingResource) or isinstance(obj, models.Invitee):
                process_id = obj.meeting.process.id
            elif isinstance(obj, models.DocumentNote) or isinstance(obj, models.Author) or isinstance(obj, models.DocumentTracking):
                process_id = obj.document.process.id
            elif isinstance(obj, models.ToRReviewer):
                process_id = obj.tor.process.id
            return can_modify_process(request.user, process_id)


class CanModifyToROrReadOnly(permissions.BasePermission):

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
            tor_id = None
            if isinstance(obj, models.TermsOfReference):
                tor_id = obj.id
            elif isinstance(obj, models.ToRReviewer):
                tor_id = obj.tor.process.id
            return can_modify_tor(request.user, tor_id)


class CanModifyToRReviewerOrReadOnly(permissions.BasePermission):

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
            if isinstance(obj, models.ToRReviewer):
                can_modify = can_modify_tor(request.user, obj.tor.id)
                is_current_reviewer = False
                if obj.tor.current_reviewer:
                    is_current_reviewer = obj.tor.current_reviewer.user == request.user

                # three ways to get object permissions:
                # 1) you are the current reviewer
                # 2) you can edit records and the record is editable or
                # 3) you can edit records and you are trying to delete a reviewer whose status is 'pending' (i.e. skipping)
                return is_current_reviewer or (can_modify and obj.can_be_modified) or (can_modify and obj.status == 30 and request.method == "DELETE")
