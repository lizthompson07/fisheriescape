from django.contrib.auth.models import User
from django.template.defaultfilters import slugify, date
from rest_framework import serializers

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

    def get_tname(self, instance):
        return instance.tname


class TravellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Traveller
        fields = "__all__"

    smart_name = serializers.SerializerMethodField()

    def get_smart_name(self, instance):
        return instance.smart_name


class TripRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripRequest1
        fields = "__all__"

    fiscal_year = serializers.StringRelatedField()
    trip_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    processing_time = serializers.SerializerMethodField()
    trip = TripSerializerLITE(read_only=True)
    created_by = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()
    status_class = serializers.SerializerMethodField()
    travellers = TravellerSerializer(many=True)

    def get_status_class(self, instance):
        return slugify(instance.get_status_display())

    def get_section(self, instance):
        return instance.section.shortish_name

    def get_created_by(self, instance):
        return instance.created_by.get_full_name()

    def get_processing_time(self, instance):
        return instance.processing_time

    def get_status_display(self, instance):
        return instance.get_status_display()

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
