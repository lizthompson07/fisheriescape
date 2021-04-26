from django.contrib.auth.models import User
from django.template.defaultfilters import date, pluralize
from django.utils.translation import gettext
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import percentage
from shared_models.api.serializers import PersonSerializer
from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class CSASRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CSASRequest
        fields = "__all__"


class MeetingSerializerLITE(serializers.ModelSerializer):
    class Meta:
        model = models.Meeting
        exclude = ["updated_at", "created_at"]  # "slug", 'author'

    display = serializers.SerializerMethodField()
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

    def get_display(self, instance):
        return str(instance)

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


class DocumentSerializer(serializers.ModelSerializer):
    # meetings = MeetingSerializerLITE(many=True)
    ttitle = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    process = serializers.StringRelatedField()
    metadata = serializers.SerializerMethodField()

    def get_metadata(self, instance):
        return instance.metadata
    def get_status_display(self, instance):
        return instance.get_status_display()

    def get_type_display(self, instance):
        return instance.get_type_display()

    def get_ttitle(self, instance):
        return instance.ttitle

    class Meta:
        model = models.Document
        fields = "__all__"


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Meeting
        exclude = ["updated_at", "created_at"]  # "slug", 'author'

    created_at_display = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    display_dates = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    start_date_display = serializers.SerializerMethodField()
    attendees = serializers.SerializerMethodField()
    length_days = serializers.SerializerMethodField()
    process = serializers.StringRelatedField()

    def get_length_days(self, instance):
        return instance.length_days

    def get_attendees(self, instance):
        my_list = list()
        for a in instance.attendees:
            my_list.append(
                get_object_or_404(models.Invitee, pk=a["invitee"]).person.full_name
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

    def get_type_display(self, instance):
        return instance.get_type_display()

    def get_created_at_display(self, instance):
        return date(instance.created_at)


class MeetingNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MeetingNote
        exclude = ["updated_at", "created_at"]  # "slug", 'author'

    type_display = serializers.SerializerMethodField()

    def get_type_display(self, instance):
        return instance.get_type_display()


class DocumentNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentNote
        exclude = ["updated_at", "created_at"]  # "slug", 'author'

    type_display = serializers.SerializerMethodField()

    def get_type_display(self, instance):
        return instance.get_type_display()


class DocumentCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentCost
        fields = "__all__"


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Author
        fields = "__all__"

    person_object = serializers.SerializerMethodField()

    def get_person_object(self, instance):
        return PersonSerializer(instance.person).data

    # type_display = serializers.SerializerMethodField()
    #
    # def get_type_display(self, instance):
    #     return instance.get_type_display()


class InviteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Invitee
        fields = "__all__"

    attendance = serializers.SerializerMethodField()
    attendance_percentage = serializers.SerializerMethodField()
    meeting_object = serializers.SerializerMethodField()
    max_date = serializers.SerializerMethodField()
    min_date = serializers.SerializerMethodField()
    person_object = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    def get_attendance(self, instance):
        return listrify([a.date.strftime("%Y-%m-%d") for a in instance.attendance.all()])

    def get_attendance_percentage(self, instance):
        return percentage(instance.attendance_fraction, 0)

    def get_meeting_object(self, instance):
        if instance.meeting:
            return MeetingSerializerLITE(instance.meeting, read_only=True).data

    def get_max_date(self, instance):
        if instance.meeting.end_date:
            return instance.meeting.end_date.strftime("%Y-%m-%d")
        elif instance.meeting.start_date:
            return instance.meeting.start_date.strftime("%Y-%m-%d")

    def get_min_date(self, instance):
        if instance.meeting.start_date:
            return instance.meeting.start_date.strftime("%Y-%m-%d")

    def get_person_object(self, instance):
        return PersonSerializer(instance.person).data

    def get_role_display(self, instance):
        return instance.get_role_display()

    def get_status_display(self, instance):
        return instance.get_status_display()


class MeetingResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MeetingResource
        fields = "__all__"

    date_added = serializers.SerializerMethodField()
    tname = serializers.SerializerMethodField()

    def get_tname(self, instance):
        return instance.tname

    def get_date_added(self, instance):
        return date(instance.created_at)
