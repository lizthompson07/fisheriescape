from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shared_models.api.serializers import RegionSerializer, DivisionSerializer, SectionSerializer
from shared_models.api.views import CurrentUserAPIView, FiscalYearListAPIView
from shared_models.models import FiscalYear, Region, Division, Section
from . import serializers
from .pagination import StandardResultsSetPagination
from .. import models, utils


class CurrentTravelUserAPIView(CurrentUserAPIView):
    def get(self, request):
        data = super().get(request).data
        data["is_regional_admin"] = utils.in_travel_admin_group(request.user)
        data["is_ncr_admin"] = utils.in_adm_admin_group(request.user)
        data["is_admin"] = utils.is_admin(request.user)
        requests = utils.get_related_requests(request.user)
        request_reviews = utils.get_trip_request_reviews(request.user)
        trip_reviews = utils.get_trip_reviews(request.user)
        # created by or traveller on a request
        data["related_requests_count"] = requests.count()
        # number of requests where review is pending (excluding those that are drafts (from children), changes_requested and pending ADM approval)
        data["request_reviews_count"] = request_reviews.count()
        data["trip_reviews_count"] = trip_reviews.count()
        # requests awaiting changes!
        data["requests_awaiting_changes"] = requests.filter(status=16).exists()
        return Response(data, status=status.HTTP_200_OK)


class TripRequestCostsListAPIView(ListAPIView):
    queryset = models.TripRequestCost.objects.all()
    serializer_class = serializers.TripRequestCostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        trip_request = models.TripRequest.objects.get(pk=self.kwargs.get("trip_request"))
        return trip_request.trip_request_costs.all()


class TripViewSet(viewsets.ModelViewSet):
    queryset = models.Conference.objects.all()
    serializer_class = serializers.TripSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = models.Conference.objects.all()
        qp = self.request.query_params
        if qp.get("adm-verification") and utils.in_adm_admin_group(self.request.user):
            qs = qs.filter(is_adm_approval_required=True, status=30)
        elif qp.get("adm-hit-list") and utils.in_adm_admin_group(self.request.user):
            qs = utils.get_adm_eligible_trips()
        elif qp.get("regional-verification") and utils.is_admin(self.request.user):
            qs = qs.filter(is_adm_approval_required=False, status=30)
        elif qp.get("all"):  # and utils.is_admin(self.request.user):  # we cannot really restrict this otherwise certain views will not work!!
            qs = qs
        else:
            qs = qs.filter(start_date__gte=timezone.now())

        filter_list = [
            'fiscal_year',
            "trip_title",
            'regional_lead',
            'adm_approval',
            'status',
            'subcategory',
        ]
        for filter in filter_list:
            input = qp.get(filter)
            if input == "true":
                input = True
            elif input == "false":
                input = False
            elif input == "null" or input == "":
                input = None

            if input is not None:
                if filter == "status":
                    qs = qs.filter(status=input)
                elif filter == "trip_title":
                    qs = qs.filter(Q(name__icontains=input) | Q(nom__icontains=input) | Q(location__icontains=input))
                elif filter == "fiscal_year":
                    qs = qs.filter(fiscal_year_id=input)
                elif filter == "regional_lead":
                    qs = qs.filter(lead_id=input)
                elif filter == "adm_approval":
                    qs = qs.filter(is_adm_approval_required=input)
                elif filter == "subcategory":
                    qs = qs.filter(trip_subcategory=input)
        return qs

    def perform_create(self, serializer):
        serializer.save(last_modified_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)


class RequestViewSet(viewsets.ModelViewSet):
    queryset = models.TripRequest1.objects.all()
    serializer_class = serializers.TripRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qp = self.request.query_params
        if qp.get("all") and utils.is_admin(self.request.user):
            qs = models.TripRequest1.objects.all()
        else:
            qs = utils.get_related_requests(self.request.user)

        filter_list = [
            "trip_title",
            'traveller',  # needs work
            'fiscal_year',
            'region',
            'division',
            'section',
            'status',
        ]
        for filter in filter_list:
            input = qp.get(filter)
            if input == "true":
                input = True
            elif input == "false":
                input = False
            elif input == "null" or input == "":
                input = None

            if input:
                if filter == "status":
                    qs = qs.filter(status=input)
                elif filter == "trip_title":
                    qs = qs.filter(Q(trip__name__icontains=input) | Q(trip__nom__icontains=input))
                # elif filter == "traveller":
                #     qs = qs.filter(project__travellers__icontains=input)
                elif filter == "fiscal_year":
                    qs = qs.filter(fiscal_year_id=input)
                elif filter == "region":
                    qs = qs.filter(section__division__branch__region_id=input)
                elif filter == "division":
                    qs = qs.filter(section__division_id=input)
                elif filter == "section":
                    qs = qs.filter(section_id=input)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)


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
