from django.contrib.auth.models import User
from django.db.models import Q
from pandas import date_range
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, ListAPIView, \
    RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dm_apps.utils import custom_send_mail
from shared_models import models as shared_models
from . import permissions, pagination
from . import serializers


# USER
#######
class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        return Response(data)


