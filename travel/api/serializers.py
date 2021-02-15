from django.contrib.auth.models import User
from django.template.defaultfilters import slugify, date
from rest_framework import serializers

from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import nz
from .. import models


# from ..utils import can_modify_project
from ..utils import can_modify_request


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

    def get_display(self, instance):
        return str(instance)

    def get_tname(self, instance):
        return instance.tname


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
    travellers = TravellerSerializer(many=True)
    trip = TripSerializerLITE(read_only=True)
    trip_display = serializers.SerializerMethodField()
    bta_attendees = serializers.SerializerMethodField()
    admin_notes_html = serializers.SerializerMethodField()

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


class TripRequestReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reviewer
        fields = "__all__"


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
