from django.contrib.auth.models import User
from django.template.defaultfilters import date, pluralize, slugify
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

    fiscal_year = serializers.StringRelatedField()
    client = serializers.StringRelatedField()
    coordinator = serializers.StringRelatedField()

    review = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    multiregional_display = serializers.SerializerMethodField()
    issue_html = serializers.SerializerMethodField()
    assistance_display = serializers.SerializerMethodField()
    rationale_html = serializers.SerializerMethodField()
    advice_needed_by_display = serializers.SerializerMethodField()
    prioritization_display = serializers.SerializerMethodField()
    submission_date_display = serializers.SerializerMethodField()
    language_display = serializers.SerializerMethodField()
    section_display = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    funding_display = serializers.SerializerMethodField()
    risk_text_html = serializers.SerializerMethodField()

    def get_risk_text_html(self, instance):
        return instance.risk_text_html

    def get_funding_display(self, instance):
        return instance.funding_display

    def get_metadata(self, instance):
        return instance.metadata

    def get_section_display(self, instance):
        return instance.section.full_name

    def get_language_display(self, instance):
        return instance.get_language_display()

    def get_submission_date_display(self, instance):
        return date(instance.submission_date)

    def get_prioritization_display(self, instance):
        return instance.prioritization_display

    def get_advice_needed_by_display(self, instance):
        return date(instance.advice_needed_by)

    def get_rationale_html(self, instance):
        return instance.rationale_html

    def get_assistance_display(self, instance):
        return instance.assistance_display

    def get_issue_html(self, instance):
        return instance.issue_html

    def get_multiregional_display(self, instance):
        return instance.multiregional_display

    def get_status_display(self, instance):
        return f'<span class=" px-1 py-1 {slugify(instance.get_status_display())}">{instance.get_status_display()}</span>'

    def get_review(self, instance):
        if hasattr(instance, "review"):
            return CSASRequestReviewSerializer(instance.review).data


class CSASRequestReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CSASRequestReview
        fields = "__all__"

    advice_date_display = serializers.SerializerMethodField()
    decision_date_display = serializers.SerializerMethodField()

    def get_advice_date_display(self, instance):
        if instance.advice_date:
            return instance.advice_date.strftime("%Y-%m-%d")

    def get_decision_date_display(self, instance):
        if instance.decision_date:
            return instance.decision_date.strftime("%Y-%m-%d")


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
    document_type = serializers.StringRelatedField()
    ttitle = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    process = serializers.StringRelatedField()
    metadata = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    tracking = serializers.SerializerMethodField()

    file_en_size = serializers.SerializerMethodField()
    tstatus_display = serializers.SerializerMethodField()

    def get_tstatus_display(self, instance):
        return instance.tstatus_display

    def get_file_en_size(self, instance):
        if instance.file_en.name:
            return f"{round((instance.file_en.size / 1000 ), 3)} kb"

    def get_tracking(self, instance):
        if hasattr(instance, "tracking"):
            return DocumentTrackingSerializer(instance.tracking).data

    def get_total_cost(self, instance):
        return instance.total_cost

    def get_metadata(self, instance):
        return instance.metadata

    def get_status_display(self, instance):
        return instance.status_display

    def get_ttitle(self, instance):
        return instance.ttitle

    class Meta:
        model = models.Document
        fields = "__all__"


class DocumentTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentTracking
        fields = "__all__"

    due_date_display = serializers.SerializerMethodField()

    def get_due_date_display(self, instance):
        if instance.due_date:
            return instance.due_date.strftime("%Y-%m-%d")

    submission_date_display = serializers.SerializerMethodField()

    def get_submission_date_display(self, instance):
        if instance.submission_date:
            return instance.submission_date.strftime("%Y-%m-%d")

    date_chair_sent_display = serializers.SerializerMethodField()

    def get_date_chair_sent_display(self, instance):
        if instance.date_chair_sent:
            return instance.date_chair_sent.strftime("%Y-%m-%d")

    date_chair_appr_display = serializers.SerializerMethodField()

    def get_date_chair_appr_display(self, instance):
        if instance.date_chair_appr:
            return instance.date_chair_appr.strftime("%Y-%m-%d")

    date_coordinator_sent_display = serializers.SerializerMethodField()

    def get_date_coordinator_sent_display(self, instance):
        if instance.date_coordinator_sent:
            return instance.date_coordinator_sent.strftime("%Y-%m-%d")

    date_coordinator_appr_display = serializers.SerializerMethodField()

    def get_date_coordinator_appr_display(self, instance):
        if instance.date_coordinator_appr:
            return instance.date_coordinator_appr.strftime("%Y-%m-%d")

    date_director_sent_display = serializers.SerializerMethodField()

    def get_date_director_sent_display(self, instance):
        if instance.date_director_sent:
            return instance.date_director_sent.strftime("%Y-%m-%d")

    date_director_appr_display = serializers.SerializerMethodField()

    def get_date_director_appr_display(self, instance):
        if instance.date_director_appr:
            return instance.date_director_appr.strftime("%Y-%m-%d")

    date_number_requested_display = serializers.SerializerMethodField()

    def get_date_number_requested_display(self, instance):
        if instance.date_number_requested:
            return instance.date_number_requested.strftime("%Y-%m-%d")

    number_approved_display = serializers.SerializerMethodField()

    def get_number_approved_display(self, instance):
        if instance.number_approved:
            return instance.number_approved.strftime("%Y-%m-%d")

    date_doc_submitted_display = serializers.SerializerMethodField()

    def get_date_doc_submitted_display(self, instance):
        if instance.date_doc_submitted:
            return instance.date_doc_submitted.strftime("%Y-%m-%d")

    date_proof_author_sent_display = serializers.SerializerMethodField()

    def get_date_proof_author_sent_display(self, instance):
        if instance.date_proof_author_sent:
            return instance.date_proof_author_sent.strftime("%Y-%m-%d")

    date_proof_author_approved_display = serializers.SerializerMethodField()

    def get_date_proof_author_approved_display(self, instance):
        if instance.date_proof_author_approved:
            return instance.date_proof_author_approved.strftime("%Y-%m-%d")

    anticipated_posting_date_display = serializers.SerializerMethodField()

    def get_anticipated_posting_date_display(self, instance):
        if instance.anticipated_posting_date:
            return instance.anticipated_posting_date.strftime("%Y-%m-%d")

    actual_posting_date_display = serializers.SerializerMethodField()

    def get_actual_posting_date_display(self, instance):
        if instance.actual_posting_date:
            return instance.actual_posting_date.strftime("%Y-%m-%d")

    updated_posting_date_display = serializers.SerializerMethodField()

    def get_updated_posting_date_display(self, instance):
        if instance.updated_posting_date:
            return instance.updated_posting_date.strftime("%Y-%m-%d")

    date_translation_sent_display = serializers.SerializerMethodField()

    def get_date_translation_sent_display(self, instance):
        if instance.date_translation_sent:
            return instance.date_translation_sent.strftime("%Y-%m-%d")

    date_returned_display = serializers.SerializerMethodField()

    def get_date_returned_display(self, instance):
        if instance.date_returned:
            return instance.date_returned.strftime("%Y-%m-%d")

    # mydate_display = serializers.SerializerMethodField()
    #
    # def get_mydate_display(self, instance):
    #     if instance.mydate:
    #         return instance.mydate.strftime("%Y-%m-%d")


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
    total_cost = serializers.SerializerMethodField()

    def get_total_cost(self, instance):
        return instance.total_cost

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

    cost_category_display = serializers.SerializerMethodField()

    def get_cost_category_display(self, instance):
        return instance.get_cost_category_display()


class MeetingCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MeetingCost
        fields = "__all__"

    cost_category_display = serializers.SerializerMethodField()

    def get_cost_category_display(self, instance):
        return instance.get_cost_category_display()


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
    roles_display = serializers.SerializerMethodField()
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

    def get_roles_display(self, instance):
        if instance.roles.exists():
            return listrify(instance.roles.all())

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
