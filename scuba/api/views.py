from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import permissions
from . import serializers
from .. import models


# USER
#######
class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        return Response(data)


# Observations
##############

class ObservationListCreateAPIView(ListCreateAPIView):
    serializer_class = serializers.ObservationSerializer
    permission_classes = [permissions.ScubaCRUDOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(section_id=self.request.data["section_id"], created_by=self.request.user)

    def get_queryset(self):
        qs = models.Observation.objects.order_by("section", "id")
        qp = self.request.query_params

        if qp.get("dive"):
            dive = get_object_or_404(models.Dive, pk=qp.get("dive"))
            qs = qs.filter(section__dive=dive)

        return qs


class ObservationRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.Observation.objects.all()
    serializer_class = serializers.ObservationSerializer
    permission_classes = [permissions.ScubaCRUDOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# Sections
##############

class SectionListCreateAPIView(ListCreateAPIView):
    serializer_class = serializers.SectionSerializer
    permission_classes = [permissions.ScubaCRUDOrReadOnly]

    def get_queryset(self):
        qs = models.Section.objects.order_by("dive", "interval")
        qp = self.request.query_params

        if qp.get("dive"):
            dive = get_object_or_404(models.Dive, pk=qp.get("dive"))
            qs = qs.filter(dive=dive)

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SectionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.Section.objects.all()
    serializer_class = serializers.SectionSerializer
    permission_classes = [permissions.ScubaCRUDOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
