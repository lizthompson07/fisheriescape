from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.template.defaultfilters import slugify, date
from rest_framework import serializers

from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import nz
from .. import models


# from ..utils import can_modify_project


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class TripRequestCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripRequestCost
        fields = "__all__"

    cost_display = serializers.SerializerMethodField()

    def get_cost_display(self, instance):
        return str(instance.cost)


class TripSerializerLITE(serializers.ModelSerializer):
    class Meta:
        model = models.Conference
        fields = "__all__"

    tname = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()
    days_until_eligible_for_adm_review = serializers.SerializerMethodField()
    time_until_eligible_for_adm_review = serializers.SerializerMethodField()

    def get_days_until_eligible_for_adm_review(self, instance):
        return instance.days_until_eligible_for_adm_review

    def get_time_until_eligible_for_adm_review(self, instance):
        return naturaltime(instance.date_eligible_for_adm_review)

    def get_display(self, instance):
        return str(instance)

    def get_tname(self, instance):
        return instance.tname


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


class TravellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Traveller
        fields = "__all__"

    smart_name = serializers.SerializerMethodField()
    traveller_info = serializers.SerializerMethodField()
    cost_breakdown_html = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    long_role = serializers.SerializerMethodField()
    role = serializers.StringRelatedField()

    def get_long_role(self, instance):
        return instance.long_role

    def get_dates(self, instance):
        return instance.dates

    def get_cost_breakdown_html(self, instance):
        return instance.cost_breakdown_html

    def get_traveller_info(self, instance):
        return instance.traveller_info

    def get_smart_name(self, instance):
        return instance.smart_name


class TripRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripRequest1
        fields = "__all__"

    created_by = serializers.SerializerMethodField()
    fiscal_year = serializers.StringRelatedField()
    processing_time = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()
    status_class = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    total_dfo_funding = serializers.SerializerMethodField()
    total_non_dfo_funding = serializers.SerializerMethodField()
    total_non_dfo_funding_sources = serializers.SerializerMethodField()
    total_request_cost = serializers.SerializerMethodField()
    travellers = TravellerSerializer(many=True, read_only=True)
    files = FileSerializer(many=True, read_only=True)
    reviewers = RequestReviewerSerializer(many=True, read_only=True)
    trip = TripSerializerLITE(read_only=True)
    trip_display = serializers.SerializerMethodField()
    bta_attendees = serializers.SerializerMethodField()
    admin_notes_html = serializers.SerializerMethodField()
    is_late_request = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    reviewer_order_message = serializers.SerializerMethodField()

    def get_reviewer_order_message(self, instance):
        return instance.reviewer_order_message

    def get_metadata(self, instance):
        return instance.metadata

    def get_is_late_request(self, instance):
        return instance.is_late_request

    def get_admin_notes_html(self, instance):
        return instance.admin_notes_html

    def get_bta_attendees(self, instance):
        return listrify(instance.bta_attendees.all())

    def get_created_by(self, instance):
        return instance.created_by.get_full_name()

    def get_processing_time(self, instance):
        return instance.processing_time

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

    fiscal_year = serializers.StringRelatedField()
    status_display = serializers.SerializerMethodField()
    status_class = serializers.SerializerMethodField()
    tname = serializers.SerializerMethodField()
    trip_subcategory = serializers.StringRelatedField()

    abstract_deadline = serializers.SerializerMethodField()
    registration_deadline = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    date_eligible_for_adm_review = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()

    def get_display(self, instance):
        return str(instance)

    def get_date_eligible_for_adm_review(self, instance):
        return date(instance.date_eligible_for_adm_review)

    def get_dates(self, instance):
        return instance.dates

    def get_registration_deadline(self, instance):
        return date(instance.registration_deadline)

    def get_abstract_deadline(self, instance):
        return date(instance.abstract_deadline)

    def get_tname(self, instance):
        return instance.tname

    def get_status_class(self, instance):
        return slugify(instance.get_status_display())

    def get_status_display(self, instance):
        return instance.get_status_display()
