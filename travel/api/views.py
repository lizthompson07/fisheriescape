from gettext import gettext as _

from django.db.models import Q
from django.template.defaultfilters import date, pluralize
from django.urls import reverse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared_models.api.serializers import RegionSerializer, DivisionSerializer, SectionSerializer
from shared_models.api.views import CurrentUserAPIView, FiscalYearListAPIView
from shared_models.models import FiscalYear, Region, Division, Section, Organization
from shared_models.utils import special_capitalize
from . import serializers
from .pagination import StandardResultsSetPagination
from .permissions import CanModifyOrReadOnly, TravelAdminOrReadOnly
from .. import models, utils


class CurrentTravelUserAPIView(CurrentUserAPIView):
    def get(self, request):
        data = super().get(request).data
        data["is_regional_admin"] = utils.in_travel_admin_group(request.user)
        data["is_ncr_admin"] = utils.in_adm_admin_group(request.user)
        data["is_admin"] = utils.is_admin(request.user)
        requests = utils.get_related_requests(request.user)
        request_reviews = utils.get_related_request_reviewers(request.user)
        trip_reviews = utils.get_related_trip_reviewers(request.user)
        # created by or traveller on a request
        data["related_requests_count"] = requests.count()
        # number of requests where review is pending (excluding those that are drafts (from children), changes_requested and pending ADM approval)
        data["request_reviews_count"] = request_reviews.count()
        data["trip_reviews_count"] = trip_reviews.count()
        # requests awaiting changes!
        data["requests_awaiting_changes"] = requests.filter(status=16).exists()

        if request.query_params.get("request"):
            my_trip_request = get_object_or_404(models.TripRequest1, pk=request.query_params.get("request"))
            data.update(utils.can_modify_request(request.user, trip_request_id=request.query_params.get("request"), as_dict=True))
            data.update(dict(is_owner=request.user.id == my_trip_request.created_by))

        return Response(data, status=status.HTTP_200_OK)


class TripViewSet(viewsets.ModelViewSet):
    queryset = models.Conference.objects.all()
    serializer_class = serializers.TripSerializer
    permission_classes = [TravelAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def post(self, request, pk):
        qp = request.query_params
        obj = get_object_or_404(models.Conference, pk=pk)
        if qp.get("reset_reviewers"):
            if utils.in_adm_admin_group(request.user):
                # This function should only ever be run if the trip is unreviewed (30 = unverified, unreviewer; 41 = verified, reviewed)
                if obj.status in [30, 41]:
                    # first remove any existing reviewers
                    obj.reviewers.all().delete()
                    # next, re-add the defaults...
                    utils.get_trip_reviewers(obj)
                else:
                    raise ValidationError(_("This function can only be used with an unreviewed trip."))
            else:
                raise ValidationError(_("You do not have the permissions to reset the reviewer list"))
            return Response(None, status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        if self.kwargs.get("pk"):
            return models.Conference.objects.filter(pk=self.kwargs.get("pk"))  # anybody can ask to see a trip.
        else:
            qs = models.Conference.objects.all()
            qp = self.request.query_params
            if qp.get("adm-verification") and utils.in_adm_admin_group(self.request.user):
                qs = qs.filter(is_adm_approval_required=True, status=30)
            elif qp.get("adm-hit-list") and utils.in_adm_admin_group(self.request.user):
                qs = utils.get_adm_eligible_trips()
            elif qp.get("regional-verification") and utils.is_admin(self.request.user):
                qs = qs.filter(is_adm_approval_required=False, status=30)
            elif qp.get("all") and utils.is_admin(self.request.user):  # we cannot really restrict this otherwise certain views will not work!!
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.TripSerializerLITE(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.TripSerializerLITE(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(last_modified_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)


class RequestViewSet(viewsets.ModelViewSet):
    queryset = models.TripRequest1.objects.all()
    serializer_class = serializers.TripRequestSerializer
    permission_classes = [CanModifyOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def post(self, request, pk):
        qp = request.query_params
        obj = get_object_or_404(models.TripRequest1, pk=pk)
        if qp.get("reset_reviewers"):
            if utils.can_modify_request(request.user, obj.id):
                # This function should only ever be run if the TR is a draft
                if obj.status == 8:
                    # first remove any existing reviewers
                    obj.reviewers.all().delete()
                    # next, re-add the defaults...
                    utils.get_request_reviewers(obj)
                else:
                    raise ValidationError(_("This function can only be used when the trip request is still a draft"))
            else:
                raise ValidationError(_("You do not have the permissions to reset the reviewer list"))
            return Response(None, status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        # if someone is looking for a specific object...
        if self.kwargs.get("pk"):
            related_ids = [r.id for r in utils.get_related_requests(self.request.user)]
            can_proceed = utils.can_modify_request(self.request.user, self.kwargs.get("pk")) or int(self.kwargs.get("pk")) in related_ids
            if can_proceed:
                return models.TripRequest1.objects.filter(pk=self.kwargs.get("pk"))
        else:
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.TripRequestSerializerLITE(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.TripRequestSerializerLITE(queryset, many=True)
        return Response(serializer.data)


class TravellerViewSet(viewsets.ModelViewSet):
    queryset = models.Traveller.objects.all()
    serializer_class = serializers.TravellerSerializer
    permission_classes = [CanModifyOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def post(self, request, pk):
        qp = request.query_params
        obj = get_object_or_404(models.Traveller, pk=pk)
        if qp.get("populate_all_costs"):
            utils.populate_traveller_costs(self.request, obj)
        elif qp.get("clear_empty_costs"):
            utils.clear_empty_traveller_costs(obj)
        return Response(None, status.HTTP_200_OK)

    def perform_create(self, serializer):
        obj = serializer.save()
        utils.populate_traveller_costs(self.request, obj)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        my_request = instance.request
        # we never want this to be used to delete a traveller from an approved trip
        if my_request.status == 11:
            raise ValidationError("Sorry, we cannot delete a traveller from an approved trip.")
        super().perform_destroy(instance)
        # if the trip is NOT in draft mode, need to provide annotation in the admin notes.
        if my_request.status != 8:
            my_request.add_admin_note(f"{date(timezone.now())}: {instance.smart_name} was removed from this request by {self.request.user.get_full_name()}")

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class ReviewerViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RequestReviewerSerializer
    permission_classes = [CanModifyOrReadOnly]
    queryset = models.Reviewer.objects.all()
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_update(self, serializer):
        # first we must determine if this is a request to skip a reviewer. If it is, the user better be an admin
        if self.request.query_params.get("skip"):
            if not utils.is_admin(self.request.user):
                raise ValidationError("Sorry this is an admin function and you are not an admin user")
            else:
                my_reviewer = serializer.instance
                my_reviewer.status = 21
                my_reviewer.status_date = timezone.now()
                my_reviewer.comments = _("Manually overridden by {user} with the following rationale: \n {comments}").format(
                    user=self.request.user,
                    comments=serializer.validated_data["comments"])
                # now we save the reviewer for real
                my_reviewer.save()
                # update any statuses if necessary
                utils.approval_seeker(my_reviewer.request, False, self.request)
        else:
            # can only change if is in draft or queued
            if serializer.instance.status in [4, 20]:
                # regular users should not be allowed to interact with RDG or ADM reviewers
                if not utils.is_admin(self.request.user) and serializer.instance.role in [5, 6]:
                    raise ValidationError(_("You do not have the necessary permission to modify this reviewer."))
                serializer.save(updated_by=self.request.user)
            else:
                # we will only tolerate interacting with the order of the reviewer
                instance = serializer.instance
                instance.order = serializer.validated_data["order"]
                instance.save()

    def perform_destroy(self, instance):
        # can only change if is in draft or queued
        if instance.status in [4, 20]:
            if not utils.is_admin(self.request.user) and instance.role in [5, 6]:
                raise ValidationError(_("You do not have the necessary permission to delete this reviewer."))
            super().perform_destroy(instance)
        else:
            raise ValidationError("cannot delete this reviewer who has the status of " + instance.get_status_display())

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        qp = request.query_params
        if qp.get("rdg") and utils.is_admin(request.user):
            qs = qs.filter(role=6, status=1).filter(~Q(request__status=16))  # rdg & pending
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        else:
            qs = utils.get_related_request_reviewers(request.user)
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)


class TripReviewerViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TripReviewerSerializer
    permission_classes = [TravelAdminOrReadOnly]
    queryset = models.TripReviewer.objects.all()
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_update(self, serializer):
        # the only type of user who should be interacting with this is an NCR admin
        if not utils.in_adm_admin_group(self.request.user):
            raise ValidationError(_("You do not have the necessary permission to modify this reviewer."))

        # first we must determine if this is a request to skip a reviewer. If it is, the user better be an admin
        if self.request.query_params.get("skip"):
            my_reviewer = serializer.instance
            my_reviewer.status = 44
            my_reviewer.status_date = timezone.now()
            my_reviewer.comments = _("Manually overridden by {user} with the following rationale: \n {comments}").format(
                user=self.request.user,
                comments=serializer.validated_data["comments"])
            # now we save the reviewer for real
            my_reviewer.save()
            # update any statuses if necessary
            utils.trip_approval_seeker(my_reviewer.trip, self.request)
        else:
            # can only change if is in draft or queued
            if serializer.instance.status in [23, 24]:
                serializer.save(updated_by=self.request.user)
            else:
                # we will only tolerate interacting with the order of the reviewer
                instance = serializer.instance
                instance.order = serializer.validated_data["order"]
                instance.save()

    def perform_destroy(self, instance):
        # can only change if is in draft or queued
        if not utils.in_adm_admin_group(self.request.user):
            raise ValidationError(_("You do not have the necessary permission to delete this reviewer."))
        if instance.status in [23, 24]:
            super().perform_destroy(instance)
        else:
            raise ValidationError("cannot delete this reviewer who has the status of " + instance.get_status_display())

    def list(self, request, *args, **kwargs):
        qs = utils.get_related_trip_reviewers(request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FileSerializer
    permission_classes = [CanModifyOrReadOnly]
    queryset = models.File.objects.all()
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class CostViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CostSerializer
    permission_classes = [CanModifyOrReadOnly]
    queryset = models.TripRequestCost.objects.all()
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("traveller"):
            traveller = get_object_or_404(models.Traveller, pk=qp.get("traveller"))
            qs = traveller.costs.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


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


def _get_labels(model):
    labels = {}
    for field in model._meta.get_fields():
        if hasattr(field, "name") and hasattr(field, "verbose_name"):
            labels[field.name] = special_capitalize(field.verbose_name)
    return labels


class RequestModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.TripRequest1

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        return Response(data)


class TripModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Conference

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        return Response(data)


class ReviewerModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Reviewer

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['role_choices'] = [dict(text=c[1], value=c[0]) for c in self.model.role_choices]
        return Response(data)


class TripReviewerModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.TripReviewer

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['role_choices'] = [dict(text=c[1], value=c[0]) for c in self.model.role_choices]
        return Response(data)


class TravellerModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Traveller

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['role_choices'] = [dict(text=item.tname, value=item.id) for item in models.Role.objects.all()]
        data['org_choices'] = [dict(text=item.full_name_and_address, value=item.full_name_and_address) for item in Organization.objects.filter(is_dfo=True)]
        return Response(data)


class FileModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.File

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        return Response(data)


class CostModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.TripRequestCost

    def get(self, request):
        data = dict()
        data['cost_choices'] = [dict(text=item.tname, value=item.id) for item in models.Cost.objects.all()]
        data['labels'] = _get_labels(self.model)
        return Response(data)


class HelpTextAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.HelpText

    def get(self, request):
        data = dict()
        for obj in models.HelpText.objects.all():
            data[obj.field_name] = str(obj)
        return Response(data)


class AdminWarningsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        msgs = list()
        anchor_txt = _("Verify now")
        if utils.is_admin(request.user):
            btn = f' &rarr; <a href="{reverse("travel:trip_list")}?regional-verification=true">{anchor_txt}</a>'

            for region in Region.objects.all():
                qs = models.Conference.objects.filter(status=30, is_adm_approval_required=False, lead=region)
                if qs.exists():
                    msgs.append(
                        # Translators: Be sure there is no space between the word 'trip' and the variable 'pluralization'
                        _("<b>ADMIN WARNING:</b> {region} Region has {unverified_trips} unverified trip{pluralization} requiring attention!!").format(
                            region=region, unverified_trips=qs.count(), pluralization=pluralize(qs.count())) + btn)

            qs = models.Conference.objects.filter(status=30, is_adm_approval_required=False, lead__isnull=True)
            if qs.exists():
                if qs.count() == 1:
                    msg = _("<b>ADMIN WARNING:</b> There is {unverified_trips} unverified trip requiring attention with <u>no regional lead</u>!!".format(
                        unverified_trips=qs.count())) + btn
                else:
                    msg = _("<b>ADMIN WARNING:</b> There are {unverified_trips} unverified trips requiring attention with <u>no regional lead</u>".format(
                        unverified_trips=qs.count())) + btn
                msgs.append(msg)

        if utils.in_adm_admin_group(request.user):
            qs = models.Conference.objects.filter(status=30, is_adm_approval_required=True)
            if qs.exists():
                btn = f' &rarr; <a href="{reverse("travel:trip_list")}?adm-verification=true">{anchor_txt}</a>'
                msgs.append(
                    # Translators: Be sure there is no space between the word 'trip' and the variable 'pluralization'
                    _("<b>ADMIN WARNING:</b> ADM Office has {unverified_trips} unverified trip{pluralization} requiring attention!!".format(
                        unverified_trips=qs.count(), pluralization=pluralize(qs.count())
                    )) + btn)
        return Response(msgs, status=status.HTTP_200_OK)
