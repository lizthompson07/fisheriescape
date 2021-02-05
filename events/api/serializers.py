from django.contrib.auth.models import User
from django.template.defaultfilters import date
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from lib.functions.custom_functions import listrify
from .. import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            "full_name"
        ]

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, instance):
        return instance.get_full_name()


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        exclude = ["updated_at", "created_at"]  # "slug", 'author'

    created_at_display = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    tname = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    display_dates = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    start_date_display = serializers.SerializerMethodField()

    attendees = serializers.SerializerMethodField()

    def get_attendees(self, instance):
        my_list = list()
        for a in instance.attendees:
            my_list.append(
                get_object_or_404(models.Invitee, pk=a["invitee"]).full_name
            )
        return listrify(my_list)

    def get_start_date_display(self, instance):
        return date(instance.start_date)

    def get_display_dates(self, instance):
        start = date(instance.start_date) if instance.start_date else "??"
        end = date(instance.end_date) if instance.end_date else "??"
        dates = f'{start} &rarr; {end}'
        return dates

    def get_dates(self, instance):
        dates = list()
        if instance.start_date:
            dates.append(instance.start_date.strftime("%Y-%m-%d"))
        if instance.end_date:
            dates.append(instance.end_date.strftime("%Y-%m-%d"))
        return dates

    def get_metadata(self, instance):
        return instance.metadata

    def get_tname(self, instance):
        return instance.tname

    def get_type_display(self, instance):
        return instance.get_type_display()

    def get_created_at_display(self, instance):
        return date(instance.created_at)


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Note
        exclude = ["updated_at", "created_at"]  # "slug", 'author'

    type_display = serializers.SerializerMethodField()

    def get_type_display(self, instance):
        return instance.get_type_display()


class InviteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Invitee
        fields = "__all__"

    status_display = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    min_date = serializers.SerializerMethodField()
    max_date = serializers.SerializerMethodField()
    attendance = serializers.SerializerMethodField()

    def get_attendance(self, instance):
        return [a.date.strftime("%Y-%m-%d") for a in instance.attendance.all()]

    def get_min_date(self, instance):
        return instance.event.start_date.strftime("%Y-%m-%d")

    def get_max_date(self, instance):
        if instance.event.end_date:
            return instance.event.end_date.strftime("%Y-%m-%d")
        return instance.event.start_date.strftime("%Y-%m-%d")

    def get_full_name(self, instance):
        return instance.full_name

    def get_status_display(self, instance):
        return instance.get_status_display()

    def get_role_display(self, instance):
        return instance.get_role_display()
