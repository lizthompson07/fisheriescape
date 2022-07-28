from django.contrib.auth.models import User
from django.template.defaultfilters import date
from django.urls import reverse
from rest_framework import serializers

from dm_apps.utils import get_timezone_time
from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class CSASRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reservation
        fields = "__all__"


class CalendarRSVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reservation
        fields = "__all__"

    resourceId = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    textColor = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    def get_color(self, instance):
        if instance.status == 1:
            return "yellow"
        elif instance.status == 30:
            return "purple"
        return "red"

    def get_textColor(self, instance):
        return "black" if instance.status == 1 else "white"

    def get_url(self, instance):
        return reverse("cars:rsvp_detail", args=[instance.id])

    def get_description(self, instance):
        return f"{instance.primary_driver.get_full_name()} ({instance.get_status_display()})<br>{date(instance.end_date)} - {date(instance.start_date)}<br>{instance.destination}"

    def get_end(self, instance):
        return get_timezone_time(instance.end_date)

    def get_start(self, instance):
        return get_timezone_time(instance.start_date)

    def get_title(self, instance):
        return f"{instance.primary_driver.get_full_name()} ({instance.get_status_display()})"

    def get_resourceId(self, instance):
        return instance.vehicle.id

