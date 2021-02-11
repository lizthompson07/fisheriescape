from django.db.models import Q
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shared_models.api.serializers import RegionSerializer, DivisionSerializer, SectionSerializer
from shared_models.api.views import CurrentUserAPIView, FiscalYearListAPIView
from shared_models.models import FiscalYear, Region, Division, Section
from . import serializers
from .. import models, utils


class CurrentTravelUserAPIView(CurrentUserAPIView):

    def get(self, request):
        data = super().get(request).data
        data["is_regional_admin"] = "travel_admin" in [group["name"] for group in data["groups"]]
        data["is_ncr_admin"] = "travel_adm_admin" in [group["name"] for group in data["groups"]]
        requests = utils.get_related_requests(request.user)
        request_reviews = utils.get_trip_request_reviews(request.user)
        trip_reviews = utils.get_trip_reviews(request.user)
        # created by or traveller on a request
        data["related_requests"] = serializers.TripRequestSerializer(requests, many=True, read_only=True).data
        # requests awaiting changes!
        data["requests_awaiting_changes"] = requests.filter(status=16).exists()
        # number of requests where review is pending (excluding those that are drafts (from children), changes_requested and pending ADM approval)
        data["request_reviews"] = serializers.TripRequestReviewerSerializer(request_reviews, many=True, read_only=True).data
        data["trip_reviews"] = serializers.TripReviewerSerializer(trip_reviews, many=True, read_only=True).data
        return Response(data, status=status.HTTP_200_OK)


#
#
# class ProjectYearRetrieveAPIView(RetrieveAPIView):
#     queryset = models.ProjectYear.objects.all().order_by("-created_at")
#     serializer_class = serializers.ProjectYearSerializer
#     permission_classes = [IsAuthenticated]
#
#
# class StaffListCreateAPIView(ListCreateAPIView):
#     queryset = models.Staff.objects.all()
#     serializer_class = serializers.StaffSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         return year.staff_set.all()
#
#     def perform_create(self, serializer):
#         serializer.save(project_year_id=self.kwargs.get("project_year"))
#
#     # def post(self, request, *args, **kwargs):
#     #     super().post(request, *args, **kwargs)
#
# class StaffRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     queryset = models.Staff.objects.all()
#     serializer_class = serializers.StaffSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#


class TripRequestCostsListAPIView(ListAPIView):
    queryset = models.TripRequestCost.objects.all()
    serializer_class = serializers.TripRequestCostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        trip_request = models.TripRequest.objects.get(pk=self.kwargs.get("trip_request"))
        return trip_request.trip_request_costs.all()


class TripListAPIView(ListAPIView):
    serializer_class = serializers.TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = models.Conference.objects.all()
        qp = self.request.query_params
        if qp.get("adm_verification"):
            return qs.filter(is_adm_approval_required=True, is_verified=False)
        if qp.get("adm_hit_list"):
            return utils.get_adm_eligible_trips()
        elif qp.get("regional_verification"):
            return qs.filter(is_adm_approval_required=False, is_verified=False)
        return qs


class RequestReviewListAPIView(ListAPIView):
    serializer_class = serializers.TripRequestReviewerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = models.Reviewer.objects.all()
        qp = self.request.query_params
        if qp.get("rdg"):
            return qs.filter(role=6, status=1).filter(~Q(request__status=16))  # rdg & pending
        return qs


# LOOKUPS
##########




class FiscalYearTravelListAPIView(FiscalYearListAPIView):

    def get_queryset(self):
        qs = FiscalYear.objects.filter(requests__isnull=False)
        return qs.distinct()


class RegionListAPIView(ListAPIView):
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Region.objects.filter(branches__divisions__sections__requests__isnull=False)
        return qs.distinct()


class DivisionListAPIView(ListAPIView):
    serializer_class = DivisionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Division.objects.filter(sections__requests__isnull=False).distinct()
        if self.request.query_params.get("region"):
            qs = qs.filter(branch__region_id=self.request.query_params.get("region"))
        return qs.distinct()


class SectionListAPIView(ListAPIView):
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Section.objects.filter(requests__isnull=False).distinct()
        if self.request.query_params.get("division"):
            qs = qs.filter(division_id=self.request.query_params.get("division"))
        elif self.request.query_params.get("region"):
            qs = qs.filter(division__branch__region_id=self.request.query_params.get("region"))
        return qs
