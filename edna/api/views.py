from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared_models.utils import get_labels
from . import serializers
from .permissions import eDNACRUDOrReadOnly
from .. import models
# USER
#######
from ..filters import SampleFilter, FilterFilter, DNAExtractFilter


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        return Response(data)


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CollectionSerializer
    permission_classes = [eDNACRUDOrReadOnly]
    queryset = models.Collection.objects.order_by("name", "start_date")


class FiltrationBatchViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FiltrationBatchSerializer
    permission_classes = [eDNACRUDOrReadOnly]
    queryset = models.FiltrationBatch.objects.all()


class ExtractionBatchViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ExtractionBatchSerializer
    permission_classes = [eDNACRUDOrReadOnly]
    queryset = models.ExtractionBatch.objects.all()


# class SampleFilter(filters.FilterSet):
#     location = filters.NumberFilter(field_name="price", lookup_expr='gte')
#     max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
#
#     class Meta:
#         model = Sample
#         fields =  ('id', "collection", "bottle_id", "location")

class SampleViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SampleSerializer
    permission_classes = [eDNACRUDOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SampleFilter
    queryset = models.Sample.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class SampleModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Sample

    def get(self, request):
        data = dict()
        data['labels'] = get_labels(self.model)
        data['sample_type_choices'] = [dict(text=item.name, value=item.id) for item in models.SampleType.objects.all()]
        # data['sample_choices'] = [dict(text=str(item), value=item.id, has_filter=item.filters.exists()) for item in
        #                           models.Sample.objects.all()]
        return Response(data)


class FilterViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FilterSerializer
    permission_classes = [eDNACRUDOrReadOnly]
    queryset = models.Filter.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterFilter

    # pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("batch"):
            batch = get_object_or_404(models.FiltrationBatch, pk=qp.get("batch"))
            qs = batch.filters.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        obj.start_datetime = obj.filtration_batch.datetime
        obj.save()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class FilterModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Filter

    def get(self, request):
        data = dict()
        data['labels'] = get_labels(self.model)
        data['filtration_type_choices'] = [dict(text=item.name, value=item.id) for item in models.FiltrationType.objects.all()]
        data['sample_choices'] = [dict(text=item.full_display, value=item.id) for item in models.Sample.objects.all()]
        return Response(data)


class DNAExtractViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.DNAExtractSerializer
    permission_classes = [eDNACRUDOrReadOnly]
    queryset = models.DNAExtract.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DNAExtractFilter

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("batch"):
            batch = get_object_or_404(models.ExtractionBatch, pk=qp.get("batch"))
            qs = batch.extracts.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        obj.save()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class DNAExtractModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.DNAExtract

    def get(self, request):
        data = dict()
        data['labels'] = get_labels(self.model)
        # we want to get a list of filters for which there has been no PCRs
        data['filter_choices'] = [dict(text=item.full_display, value=item.id, has_extract=hasattr(item, 'extract')) for item in models.Filter.objects.all()]
        data['dna_extraction_protocol_choices'] = [dict(text=item.name, value=item.id) for item in models.DNAExtractionProtocol.objects.all()]

        return Response(data)


class PCRViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PCRSerializer
    permission_classes = [eDNACRUDOrReadOnly]
    queryset = models.PCR.objects.all()

    # pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("batch"):
            batch = get_object_or_404(models.PCRBatch, pk=qp.get("batch"))
            qs = batch.pcrs.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        raise ValidationError(_("You need to specify a batch"))

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        obj.start_datetime = obj.pcr_batch.datetime
        obj.save()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class PCRModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.PCR

    def get(self, request):
        data = dict()
        data['labels'] = get_labels(self.model)
        # we want to get a list of filters for which there has been no PCRs
        data['extract_choices'] = [dict(text=item.full_display, value=item.id) for item in models.DNAExtract.objects.all()]
        data['master_mix_choices'] = [dict(text=str(item), value=item.id) for item in models.MasterMix.objects.all()]
        return Response(data)


class PCRAssayModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.PCRAssay

    def get(self, request):
        data = dict()
        data['labels'] = get_labels(self.model)
        data['assay_choices'] = [dict(text=str(item), value=item.id) for item in models.Assay.objects.all()]
        return Response(data)


class PCRAssayViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PCRAssaySerializer
    permission_classes = [eDNACRUDOrReadOnly]
    queryset = models.PCRAssay.objects.all()

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("batch"):
            batch = get_object_or_404(models.PCRBatch, pk=qp.get("batch"))
            qs = models.PCRAssay.objects.filter(pcr__pcr_batch=batch)
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        raise ValidationError(_("You need to specify a batch"))

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        obj.save()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

# class SpeciesObservationViewSet(viewsets.ModelViewSet):
#     serializer_class = serializers.SpeciesObservationSerializer
#     permission_classes = [eDNACRUDOrReadOnly]
#     queryset = models.SpeciesObservation.objects.all()
#
#     # pagination_class = StandardResultsSetPagination
#
#     def list(self, request, *args, **kwargs):
#         qp = request.query_params
#         if qp.get("pcr"):
#             pcr = get_object_or_404(models.PCR, pk=qp.get("pcr"))
#             qs = pcr.observations.all()
#             serializer = self.get_serializer(qs, many=True)
#             return Response(serializer.data)
#         raise ValidationError(_("You need to specify a PCR"))
#
#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user, updated_by=self.request.user)
#
#     def perform_update(self, serializer):
#         serializer.save(updated_by=self.request.user)
#
#
# class SpeciesObservationModelMetaAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#     model = models.SpeciesObservation
#
#     def get(self, request):
#         data = dict()
#         data['labels'] = get_labels(self.model)
#         # we want to get a list of filters for which there has been no SpeciesObservations
#         data['species_choices'] = [dict(text=str(item), value=item.id) for item in models.Species.objects.all()]
#         return Response(data)
