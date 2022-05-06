import sys

from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from shared_models.utils import special_capitalize, get_labels
from . import serializers
# USER
#######
from .pagination import StandardResultsSetPagination
from .permissions import IsAdminOrReadOnly
from .. import models


def _get_labels(model):
    labels = {}
    for field in model._meta.get_fields():
        if hasattr(field, "name") and hasattr(field, "verbose_name"):
            labels[field.name] = special_capitalize(field.verbose_name)
    return labels


class UserListAPIView(ListAPIView):
    queryset = User.objects.filter(first_name__isnull=False, last_name__isnull=False).filter(
        ~Q(first_name__exact="") & ~Q(last_name__exact="")
    ).order_by("first_name", "last_name")
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email', 'id']


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.CurrentUserSerializer(instance=request.user)
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)


class RegionViewSet(ModelViewSet):
    queryset = models.Region.objects.order_by("name")
    serializer_class = serializers.RegionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(last_modified_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)


class SectorViewSet(ModelViewSet):
    queryset = models.Sector.objects.order_by("region__name", "name")
    serializer_class = serializers.SectorSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['region']

    def perform_create(self, serializer):
        serializer.save(last_modified_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)


class BranchViewSet(ModelViewSet):
    queryset = models.Branch.objects.order_by("region__name", "name")
    serializer_class = serializers.BranchSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sector__region', "sector"]

    def perform_create(self, serializer):
        serializer.save(last_modified_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)


class DivisionViewSet(ModelViewSet):
    queryset = models.Division.objects.order_by("branch__region__name", "branch__name", "name")
    serializer_class = serializers.DivisionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['branch__sector__region', "branch__sector", "branch"]

    def perform_create(self, serializer):
        serializer.save(last_modified_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)


class SectionViewSet(ModelViewSet):
    queryset = models.Section.objects.order_by("division__branch__region__name", "division__branch__name", "division__name", "name")
    serializer_class = serializers.SectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['division__branch__sector__region', "division__branch__sector", "division__branch", "division"]

    def perform_create(self, serializer):
        serializer.save(last_modified_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)


# LOOKUPS
##########


class FiscalYearListAPIView(ListAPIView):
    serializer_class = serializers.FiscalYearSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.FiscalYear.objects.all()


# class RegionListAPIView(ListAPIView):
#     serializer_class = serializers.RegionSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         qs = Region.objects.filter(branches__divisions__sections__requests__isnull=False)
#         return qs.distinct()
#
#
# class DivisionListAPIView(ListAPIView):
#     serializer_class = serializers.DivisionSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         qs = Division.objects.filter(sections__requests__isnull=False).distinct()
#         if self.request.query_params.get("region"):
#             qs = qs.filter(branch__region_id=self.request.query_params.get("region"))
#         return qs.distinct()
#
#
# class SectionListAPIView(ListAPIView):
#     serializer_class = serializers.SectionSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         qs = Section.objects.filter(requests__isnull=False).distinct()
#         if self.request.query_params.get("division"):
#             qs = qs.filter(division_id=self.request.query_params.get("division"))
#         elif self.request.query_params.get("region"):
#             qs = qs.filter(division__branch__region_id=self.request.query_params.get("region"))
#         return qs


class RegionListAPIView(ListAPIView):
    serializer_class = serializers.RegionSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.Region.objects.all()


class DivisionListAPIView(ListAPIView):
    serializer_class = serializers.DivisionSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.Division.objects.all()


class SectionListAPIView(ListAPIView):
    serializer_class = serializers.SectionSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.Section.objects.all()


class SharedModelMetadataAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = None
    data = None

    def get_model(self):
        qp = self.request.GET
        if not qp.get("app_name"):
            raise ValidationError(_("Missing the 'app_name' parameter"))
        if not qp.get("model_name"):
            raise ValidationError(_("Missing the 'model_name' parameter"))
        app_name = qp.get("app_name")
        model_name = qp.get("model_name")
        if not sys.modules.get(app_name):
            raise ValidationError(_("Please check the app name. The app module '{}' was not found.").format(app_name))
        app_mod = sys.modules[app_name]
        if not hasattr(app_mod, "models"):
            raise ValidationError(_("The 'models' module was not found in app '{}'.").format(app_name))
        model_mod = getattr(app_mod, "models")
        if not hasattr(model_mod, model_name):
            raise ValidationError(_("Please check the model name. Model '{}' not found in the '{}' module.").format(model_name, model_mod))
        return getattr(model_mod, model_name)

    def get_display_mode(self):
        qp = self.request.GET
        if qp.get("as_choices") and (qp.get("as_choices").lower() == "true" or qp.get("as_choices") == "1"):
            return "choices"

    def get_data(self):
        data = dict()
        model = self.get_model()
        if self.get_display_mode() == "choices":
            data['choices'] = [dict(text=str(item), value=item.id) for item in model.objects.all()]
        else:
            data['labels'] = get_labels(model)
            for field in model._meta.get_fields():
                if hasattr(field, "choices") and getattr(field, "choices"):
                    data[f'{field.name}_choices'] = [dict(text=c[1], value=c[0]) for c in getattr(field, "choices")]
        return data

    def get(self, request):
        data = self.get_data()
        return Response(data, status=status.HTTP_200_OK)
