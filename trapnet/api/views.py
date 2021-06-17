from django.utils.translation import gettext
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from shared_models.api.views import _get_labels
from . import serializers
from .permissions import TrapnetCRUDOrReadOnly
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

class ObservationViewSet(ModelViewSet):
    queryset = models.Observation.objects.order_by("-id")
    serializer_class = serializers.ObservationSerializer
    permission_classes = [TrapnetCRUDOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("sample"):
            sample = get_object_or_404(models.Sample, pk=qp.get("sample"))
            qs = sample.observations.order_by("species", "-tag_number")
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        elif qp.get("sweep"):
            sweep = get_object_or_404(models.Sweep, pk=qp.get("sweep"))
            qs = sweep.observations.order_by("species", "-tag_number")
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        if qp.get("get_labels"):
            data = dict()
            data['labels'] = _get_labels(self.queryset.model)
            species_choices = [dict(text=obj.search_name, value=obj.id) for obj in models.Species.objects.all()]
            species_choices.insert(0, dict(text="-----", value=None))
            data['species_choices'] = species_choices
            status_choices = [dict(text=obj.choice, value=obj.id) for obj in models.Status.objects.all()]
            status_choices.insert(0, dict(text="-----", value=None))
            data['status_choices'] = status_choices
            origin_choices = [dict(text=obj.choice, value=obj.id) for obj in models.Origin.objects.all()]
            origin_choices.insert(0, dict(text="-----", value=None))
            data['origin_choices'] = origin_choices
            sex_choices = [dict(text=obj.choice, value=obj.id) for obj in models.Sex.objects.all()]
            sex_choices.insert(0, dict(text="-----", value=None))
            data['sex_choices'] = sex_choices
            return Response(data)
        raise ValidationError(gettext("You need to specify a sample"))
