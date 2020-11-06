from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from ecosystem_survey import models as es_models


# class BasketInActiveSetOrReadOnly(permissions.BasePermission):
#     '''catch should belong to the active set or view should be  read only'''
#     def has_permission(self, request, view):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         basket = get_object_or_404(es_models.Basket, view.kwargs.get("pk"))
#         if basket

class IsSuperuser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser


class IsOceanUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.profile.oceanography
