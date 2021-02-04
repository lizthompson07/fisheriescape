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
from shapely.geometry import Point, Polygon

from dm_apps.utils import custom_send_mail
from shared_models import models as shared_models
from . import permissions, pagination
from . import serializers
from .. import models


# USER
#######
class CurrentPublicationUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        return Response(data)


# Pubs
#######
class PubsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lat =lon = False
        if request.query_params.get("lat"):
            lat = float(request.query_params.get("lat"))
        if request.query_params.get("lon"):
            lon = float(request.query_params.get("lon"))

        geoscope_instaces = models.GeographicScope.objects.all()
        proj_instances = models.Project.objects.all()
        poly_qs = [models.Polygon.objects.filter(geoscope=gs.pk) for gs in geoscope_instaces]
        poly_dict = {}
        for poly in poly_qs:
            if len(poly) > 2:
                pt_list = [(pt.latitude, pt.longitude) for pt in poly]
                poly_dict[str(poly[0].geoscope.pk)] = Polygon(pt_list)

        if lat and lon:
            pt = Point(lat, lon)
            proj_instances = models.Project.objects.none()
            for geoscope, polygon in poly_dict.items():
                if polygon.contains(pt):
                    proj_instances = proj_instances | models.Project.objects.filter(geographic_scope=int(geoscope))

        proj_instances = proj_instances.filter().distinct()

        serializer = serializers.PubsDisplaySerializer(instance=proj_instances, many=True)
        data = serializer.data
        return Response(data)


