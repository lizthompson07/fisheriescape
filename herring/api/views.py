import numpy as np
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared_models.api.views import SharedModelMetadataAPIView
from . import serializers
from .permissions import herringCRUDOrReadOnly
from .. import models
from ..utils import make_fish_flags


# USER
#######


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        return Response(data)


class LengthFrequencyViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.LengthFrequencySerializer
    permission_classes = [herringCRUDOrReadOnly]
    queryset = models.LengthFrequency.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sample', ]


class FishDetailViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FishDetailSerializer
    permission_classes = [herringCRUDOrReadOnly]
    queryset = models.FishDetail.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sample', ]


    def perform_update(self, serializer):
        obj = serializer.save()
        make_fish_flags(obj, self.request.user)

class SampleViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.LengthFrequencySerializer
    permission_classes = [herringCRUDOrReadOnly]
    queryset = models.LengthFrequency.objects.all()

    def post(self, request, pk):
        self.check_permissions(request)
        qp = request.query_params
        if qp.get("purge"):
            sample = get_object_or_404(models.Sample, pk=pk)
            sample.length_frequency_objects.all().delete()
            return Response(None, status.HTTP_204_NO_CONTENT)
        if qp.get("seed"):
            try:
                sample = get_object_or_404(models.Sample, pk=pk)
                min_len = float(request.data.get("min"))
                max_len = float(request.data.get("max"))
                bin_int = float(request.data.get("int"))
                num = int((max_len - min_len) / bin_int)+1

                for i in np.linspace(min_len, max_len, num):
                    # create a new lf
                    models.LengthFrequency.objects.create(
                        sample=sample,
                        length_bin_id=i,
                        count=0
                    )

                return Response(None, status.HTTP_204_NO_CONTENT)
            except Exception as e:
                raise ValidationError(f"Sorry, something went wrong: {e}")

        raise ValidationError(_("This endpoint cannot be used without a query param"))




class HerringModelMetadataAPIView(SharedModelMetadataAPIView):
    def get_data(self):
        data = super().get_data()
        model = self.get_model()

        return data
