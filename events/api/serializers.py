from django.template.defaultfilters import date, pluralize
from django.utils.translation import gettext
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import percentage
from .. import models


class EventSerializerLITE(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        exclude = ["updated_at", "created_at"]  # "slug", 'author'

    tname = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    display_dates = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    start_date_display = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()

    def get_start_date_display(self, instance):
        return date(instance.start_date)

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

    def get_display_dates(self, instance):
        start = date(instance.start_date) if instance.start_date else "??"
        dates = f'{start}'
        if instance.end_date and instance.end_date != instance.start_date:
            end = date(instance.end_date)
            dates += f' &rarr; {end}'
        days_display = "{} {}{}".format(instance.length_days, gettext("day"), pluralize(instance.length_days))
        dates += f' ({days_display})'
        return dates


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
    length_days = serializers.SerializerMethodField()
    parent_event_display = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    def get_children(self, instance):
        return EventSerializerLITE(instance.children.all(), many=True, read_only=True).data

    def get_parent_event_display(self, instance):
        if instance.parent_event:
            return EventSerializer(instance.parent_event, read_only=True).data

    def get_length_days(self, instance):
        return instance.length_days

    def get_attendees(self, instance):
        my_list = list()
        for a in instance.attendees:
            my_list.append(
                get_object_or_404(models.Invitee, pk=a["invitee"]).full_name
            )
        if len(my_list):
            return listrify(my_list)
        return gettext("None")

    def get_start_date_display(self, instance):
        return date(instance.start_date)

    def get_display_dates(self, instance):
        return instance.display_dates

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
    attendance_percentage = serializers.SerializerMethodField()
    event_object = serializers.SerializerMethodField()

    def get_event_object(self, instance):
        if instance.event:
            return EventSerializerLITE(instance.event, read_only=True).data

    def get_attendance_percentage(self, instance):
        return percentage(instance.attendance_fraction, 0)

    def get_attendance(self, instance):
        return [a.date.strftime("%Y-%m-%d") for a in instance.attendance.all()]

    def get_min_date(self, instance):
        if instance.event.start_date:
            return instance.event.start_date.strftime("%Y-%m-%d")

    def get_max_date(self, instance):
        if instance.event.end_date:
            return instance.event.end_date.strftime("%Y-%m-%d")
        elif instance.event.start_date:
            return instance.event.start_date.strftime("%Y-%m-%d")

    def get_full_name(self, instance):
        return instance.full_name

    def get_status_display(self, instance):
        return instance.get_status_display()

    def get_role_display(self, instance):
        return instance.get_role_display()


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Resource
        fields = "__all__"

    date_added = serializers.SerializerMethodField()
    tname = serializers.SerializerMethodField()

    def get_tname(self, instance):
        return instance.tname

    def get_date_added(self, instance):
        return date(instance.created_at)
