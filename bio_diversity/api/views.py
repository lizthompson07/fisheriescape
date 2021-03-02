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
from .. import models


# USER
#######
class BioCurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        return Response(data)


# Individual
#######
class IndividualAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        indv_instances = models.Individual.objects.all()
        if request.query_params.get("pit_tag"):
            pit_tag = request.query_params.get("pit_tag")
            indv_instances = indv_instances.filter(pit_tag__icontains=pit_tag).distinct()
        if request.query_params.get("length"):
            length = request.query_params.get("length")
            indv_instances = indv_instances.filter(animal_details__individual_details__anidc_id_id=2,
                                                   animal_details__individual_details__det_val__gte=length).distinct()

        serializer = serializers.IndividualDisplaySerializer(instance=indv_instances, many=True)
        data = serializer.data
        return Response(data)


