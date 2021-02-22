from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Q
from django.template.defaultfilters import slugify, date
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import nz
from .. import models
# from ..utils import can_modify_project
from ..utils import get_cost_comparison


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class TripSerializerLITE(serializers.ModelSerializer):
    class Meta:
        model = models.Conference
        fields = "__all__"

    abstract_deadline = serializers.SerializerMethodField()
    adm_review_deadline = serializers.SerializerMethodField()
    date_eligible_for_adm_review = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    days_until_adm_review_deadline = serializers.SerializerMethodField()
    days_until_eligible_for_adm_review = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    fiscal_year = serializers.StringRelatedField()
    lead = serializers.StringRelatedField()
    registration_deadline = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    status_class = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    time_until_eligible_for_adm_review = serializers.SerializerMethodField()
    tname = serializers.SerializerMethodField()
    traveller_count = serializers.SerializerMethodField()
    trip_subcategory = serializers.StringRelatedField()

    def get_abstract_deadline(self, instance):
        return instance.abstract_deadline.strftime("%Y-%m-%d") if instance.abstract_deadline else None

    def get_adm_review_deadline(self, instance):
        return instance.adm_review_deadline.strftime("%Y-%m-%d") if instance.adm_review_deadline else None

    def get_date_eligible_for_adm_review(self, instance):
        return instance.date_eligible_for_adm_review.strftime("%Y-%m-%d") if instance.date_eligible_for_adm_review else None

    def get_dates(self, instance):
        return instance.dates

    def get_days_until_adm_review_deadline(self, instance):
        return instance.days_until_adm_review_deadline

    def get_days_until_eligible_for_adm_review(self, instance):
        return instance.days_until_eligible_for_adm_review

    def get_display(self, instance):
        return str(instance)

    def get_end_date(self, instance):
        return instance.end_date.strftime("%Y-%m-%d")

    def get_registration_deadline(self, instance):
        return instance.registration_deadline.strftime("%Y-%m-%d") if instance.registration_deadline else None

    def get_start_date(self, instance):
        return instance.start_date.strftime("%Y-%m-%d")

    def get_status_class(self, instance):
        return slugify(instance.get_status_display())

    def get_status_display(self, instance):
        return instance.get_status_display()

    def get_time_until_eligible_for_adm_review(self, instance):
        return naturaltime(instance.date_eligible_for_adm_review)

    def get_tname(self, instance):
        return instance.tname

    def get_traveller_count(self, instance):
        return instance.travellers.count()


class TripRequestSerializerLITE(serializers.ModelSerializer):
    class Meta:
        model = models.TripRequest1
        fields = "__all__"

    created_by = serializers.SerializerMethodField()
    is_late_request = serializers.SerializerMethodField()
    processing_time = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    status_class = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    trip_display = serializers.SerializerMethodField()
    traveller_count = serializers.SerializerMethodField()
    trip = TripSerializerLITE(read_only=True)
    section = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()

    def get_display(self, instance):
        return str(instance)

    def get_section(self, instance):
        return instance.section.shortish_name

    def get_traveller_count(self, instance):
        return instance.travellers.count()

    def get_created_by(self, instance):
        if instance.created_by:
            return instance.created_by.get_full_name()

    def get_is_late_request(self, instance):
        return instance.is_late_request

    def get_processing_time(self, instance):
        return instance.processing_time

    def get_region(self, instance):
        return instance.section.division.branch.region.tname

    def get_status_class(self, instance):
        return slugify(instance.get_status_display())

    def get_status_display(self, instance):
        return instance.get_status_display()

    def get_trip_display(self, instance):
        return str(instance.trip)


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = "__all__"

    date_created = serializers.SerializerMethodField()

    def get_date_created(self, instance):
        return date(instance.date_created)


class RequestReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reviewer
        exclude = ["trip_request", ]

    role_display = serializers.SerializerMethodField()
    status_date = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    user_display = serializers.SerializerMethodField()
    status_class = serializers.SerializerMethodField()
    comments_html = serializers.SerializerMethodField()
    request = TripRequestSerializerLITE(read_only=True)

    def get_comments_html(self, instance):
        return instance.comments_html

    def get_status_class(self, instance):
        return slugify(instance.get_status_display())

    def get_role_display(self, instance):
        return instance.get_role_display()

    def get_status_date(self, instance):
        return date(instance.status_date)

    def get_status_display(self, instance):
        return instance.get_status_display()

    def get_user_display(self, instance):
        return instance.user.get_full_name() if instance.user else None


class CostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripRequestCost
        fields = "__all__"

    cost_display = serializers.SerializerMethodField()

    def get_cost_display(self, instance):
        return str(instance.cost)


class TravellerSerializer(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(format=None, input_formats=None, required=False, allow_null=True)
    end_date = serializers.DateTimeField(format=None, input_formats=None, required=False, allow_null=True)
    costs = CostSerializer(many=True, read_only=True)

    class Meta:
        model = models.Traveller
        fields = "__all__"

    cost_breakdown_html = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    long_role = serializers.SerializerMethodField()
    non_dfo_costs_html = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    smart_name = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    traveller_info = serializers.SerializerMethodField()
    request_obj = serializers.SerializerMethodField()

    def get_role_display(self, instance):
        return str(instance.role)

    def get_request_obj(self, instance):
        return TripRequestSerializerLITE(instance.request).data

    def get_cost_breakdown_html(self, instance):
        return instance.cost_breakdown_html

    def get_dates(self, instance):
        return instance.dates

    def get_long_role(self, instance):
        return instance.long_role

    def get_non_dfo_costs_html(self, instance):
        return instance.non_dfo_costs_html

    def get_smart_name(self, instance):
        return instance.smart_name

    def get_total_cost(self, instance):
        return instance.total_cost

    def get_traveller_info(self, instance):
        return instance.traveller_info

    def validate(self, attrs):
        """
        form validation:
        - make sure that the user is not already attending this trip!
        - make sure that the request start date and the trip start date make sense with respect to each other and individually
        """
        trip_request = attrs.get("request")
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        user = attrs.get("user")
        trip = trip_request.trip
        trip_start_date = trip.start_date
        trip_end_date = trip.end_date

        # make sure that the user is not already attending this trip from another request!
        if user and models.Traveller.objects.filter(~Q(request=trip_request)).filter(request__trip=trip, user=user).exists():
            msg = _('This user is cannot be added here because they are listed on another request!')
            raise ValidationError(msg)

        # first, let's look at the request date and make sure it makes sense, i.e. start date is before end date and
        # the length of the trip is not too long
        if start_date and end_date:
            if end_date < start_date:
                msg = _('The start date of the trip must occur before the end date.')
                raise ValidationError(msg)
            if abs((start_date - end_date).days) > 180:
                msg = _('The length of this trip is unrealistic.')
                raise ValidationError(msg)
            # is the start date of the travel request equal to or before the start date of the trip?
            if trip_start_date:
                delta = abs(start_date - trip_start_date)
                if delta.days > 10:
                    msg = _(
                        "The start date of this request ({start_date}) has to be within 10 days of the start date of the selected trip ({trip_start_date})!").format(
                        start_date=start_date.strftime("%Y-%m-%d"),
                        trip_start_date=trip_start_date.strftime("%Y-%m-%d"),
                    )
                    raise ValidationError(msg)

            # is the end_date of the travel request equal to or after the end date of the trip?
            if trip_end_date:
                delta = abs(end_date - trip_end_date)
                if delta.days > 10:
                    msg = _(
                        "The end date of this request ({end_date}) must be within 10 days of the end date of the selected trip ({trip_end_date})!").format(
                        end_date=end_date.strftime("%Y-%m-%d"),
                        trip_end_date=trip_end_date.strftime("%Y-%m-%d"),
                    )
                    raise ValidationError(msg)
        return attrs


class TripRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripRequest1
        fields = "__all__"

    admin_notes_html = serializers.SerializerMethodField()
    bta_attendees = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()
    files = FileSerializer(many=True, read_only=True)
    fiscal_year = serializers.StringRelatedField()
    is_late_request = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    processing_time = serializers.SerializerMethodField()
    reviewer_order_message = serializers.SerializerMethodField()
    reviewers = RequestReviewerSerializer(many=True, read_only=True)
    section = serializers.SerializerMethodField()
    status_class = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    total_dfo_funding = serializers.SerializerMethodField()
    total_non_dfo_funding = serializers.SerializerMethodField()
    total_non_dfo_funding_sources = serializers.SerializerMethodField()
    total_request_cost = serializers.SerializerMethodField()
    travellers = TravellerSerializer(many=True, read_only=True)
    trip = TripSerializerLITE(read_only=True)
    trip_display = serializers.SerializerMethodField()
    original_submission_date = serializers.SerializerMethodField()

    cost_comparison = serializers.SerializerMethodField()

    def get_cost_comparison(self, instance):
        return get_cost_comparison(instance.travellers.all())

    def get_original_submission_date(self, instance):
        return date(instance.original_submission_date)

    def get_admin_notes_html(self, instance):
        return instance.admin_notes_html

    def get_bta_attendees(self, instance):
        return listrify(instance.bta_attendees.all())

    def get_created_by(self, instance):
        if instance.created_by:
            return instance.created_by.get_full_name()

    def get_display(self, instance):
        return str(instance)

    def get_is_late_request(self, instance):
        return instance.is_late_request

    def get_metadata(self, instance):
        return instance.metadata

    def get_processing_time(self, instance):
        return instance.processing_time

    def get_reviewer_order_message(self, instance):
        return instance.reviewer_order_message

    def get_section(self, instance):
        return instance.section.shortish_name

    def get_status_class(self, instance):
        return slugify(instance.get_status_display())

    def get_status_display(self, instance):
        return instance.get_status_display()

    def get_total_dfo_funding(self, instance):
        return instance.total_dfo_funding

    def get_total_non_dfo_funding(self, instance):
        return instance.total_non_dfo_funding

    def get_total_non_dfo_funding_sources(self, instance):
        return nz(instance.total_non_dfo_funding_sources)

    def get_total_request_cost(self, instance):
        return instance.total_request_cost

    def get_trip_display(self, instance):
        return instance.trip.tname


class TripReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripReviewer
        fields = "__all__"


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Conference
        fields = "__all__"

    abstract_deadline = serializers.SerializerMethodField()
    admin_notes_html = serializers.SerializerMethodField()
    cost_comparison = serializers.SerializerMethodField()
    date_eligible_for_adm_review = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()
    fiscal_year = serializers.StringRelatedField()
    lead = serializers.StringRelatedField()
    registration_deadline = serializers.SerializerMethodField()
    status_class = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    tname = serializers.SerializerMethodField()
    travellers = serializers.SerializerMethodField()
    trip_subcategory = serializers.StringRelatedField()
    adm_review_deadline = serializers.SerializerMethodField()
    time_until_adm_review_deadline = serializers.SerializerMethodField()
    days_until_adm_review_deadline = serializers.SerializerMethodField()
    requests = TripRequestSerializerLITE(many=True, read_only=True)
    metadata = serializers.SerializerMethodField()

    def get_metadata(self, instance):
        return instance.metadata

    def get_days_until_adm_review_deadline(self, instance):
        return instance.days_until_adm_review_deadline

    def get_time_until_adm_review_deadline(self, instance):
        return naturaltime(instance.adm_review_deadline)

    def get_adm_review_deadline(self, instance):
        return date(instance.adm_review_deadline)

    def get_abstract_deadline(self, instance):
        return date(instance.abstract_deadline)

    def get_admin_notes_html(self, instance):
        return instance.admin_notes_html

    def get_cost_comparison(self, instance):
        return get_cost_comparison(instance.travellers)

    def get_date_eligible_for_adm_review(self, instance):
        return date(instance.date_eligible_for_adm_review)

    def get_dates(self, instance):
        return instance.dates

    def get_display(self, instance):
        return str(instance)

    def get_registration_deadline(self, instance):
        return date(instance.registration_deadline)

    def get_status_class(self, instance):
        return slugify(instance.get_status_display())

    def get_status_display(self, instance):
        return instance.get_status_display()

    def get_tname(self, instance):
        return instance.tname

    def get_travellers(self, instance):
        return TravellerSerializer(instance.travellers, many=True, read_only=True).data
