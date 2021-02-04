from django.contrib.auth.models import User
from django.template.defaultfilters import date
from rest_framework import serializers

from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "is_admin", "is_management", "is_rds"]


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

    notes = serializers.SerializerMethodField()

    def get_notes(self, instance):
        return NoteSerializer(instance.notes, many=True, read_only=True).data

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
