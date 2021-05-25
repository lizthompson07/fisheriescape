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
############################
class BioCurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        return Response(data)


# Bio api view
############################
class BioAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = None
    model_instances = None

    def get(self, request):
        self.model_instances = self.model.objects.all()
        if request.query_params.get("pk"):
            pk = request.query_params.get("pk")
            self.model_instances = self.model_instances.filter(pk=pk).distinct()


# Individual
############################
class IndividualAPIView(BioAPIView):
    model = models.Individual

    def get(self, request):
        super().get(request)
        if request.query_params.get("pit_tag"):
            pit_tag = request.query_params.get("pit_tag")
            self.model_instances = self.model_instances.filter(pit_tag__icontains=pit_tag).distinct()
        if request.query_params.get("length"):
            length = request.query_params.get("length")
            self.model_instances = self.model_instances.filter(animal_details__individual_details__anidc_id_id=2,
                                                   animal_details__individual_details__det_val__gte=length).distinct()

        serializer = serializers.IndividualDisplaySerializer(instance=self.model_instances, many=True)
        data = serializer.data
        return Response(data)


# Cup
############################
class CupAPIView(BioAPIView):
    model = models.Cup

    def get(self, request):
        super().get(request)

        if request.query_params.get("name"):
            name = request.query_params.get("name")
            self.model_instances = self.model_instances.filter(name__iexact=name).distinct()

        serializer = serializers.CupDisplaySerializer(instance=self.model_instances, many=True)
        data = serializer.data
        return Response(data)


# Anix
############################
class AnixAPIView(BioAPIView):
    model = models.AniDetailXref

    def get(self, request):
        super().get(request)

        cont_type_dict = {"event": "evnt_id", "indv": "indv_id", "group": "grp_id", "contx": "contx_id",
                          "loc": "loc_id", "pair": "pair_id"}

        for key, value in cont_type_dict.items():
            if request.query_params.get(key):
                obj_pk = request.query_params.get(key)
                filter_dict = {value: obj_pk}
                self.model_instances = self.model_instances.filter(**filter_dict).distinct()

        serializer = serializers.AnixDisplaySerializer(instance=self.model_instances, many=True)
        data = serializer.data
        return Response(data)


# Contx
############################
class ContxAPIView(BioAPIView):
    model = models.ContainerXRef

    def get(self, request):
        super().get(request)

        cont_type_dict = {"cup": "cup_id", "drawer": "draw_id", "heath_unit": "heat_id", "tank": "tank_id",
                          "tray": "tray_id", "trough": "trof_id"}

        for key, value in cont_type_dict.items():
            if request.query_params.get(key):

                cont_pk = request.query_params.get(key)
                filter_dict = {value: cont_pk}
                self.model_instances = self.model_instances.filter(**filter_dict).distinct()

        serializer = serializers.ContxDisplaySerializer(instance=self.model_instances, many=True)
        data = serializer.data
        return Response(data)


# Count
############################
class CountAPIView(BioAPIView):
    model = models.Count

    def get(self, request):
        super().get(request)

        if request.query_params.get("group"):
            grp_pk = request.query_params.get("group")
            anix_set = models.AniDetailXref.objects.filter(grp_id=grp_pk, contx_id__isnull=False).select_related('contx_id')
            contx_list = [anix.contx_id for anix in anix_set]
            self.model_instances = self.model_instances.filter(contx_id__in=contx_list).distinct()
        serializer = serializers.CntDisplaySerializer(instance=self.model_instances, many=True)
        data = serializer.data
        return Response(data)


# Group
############################
class GroupAPIView(BioAPIView):
    model = models.Group

    def get(self, request):
        super().get(request)
        if request.query_params.get("stock"):
            stock = request.query_params.get("stock")
            self.model_instances = self.model_instances.filter(stok_id__name__icontains=stock).distinct()
        if request.query_params.get("year"):
            year = request.query_params.get("year")
            self.model_instances = self.model_instances.filter(grp_year=year).distinct()
        if request.query_params.get("col"):
            coll = request.query_params.get("col")
            self.model_instances = self.model_instances.filter(coll_id__name__icontains=coll).distinct()

        serializer = serializers.GroupDisplaySerializer(instance=self.model_instances, many=True)
        data = serializer.data
        return Response(data)
