from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Q
from django.template.defaultfilters import date, pluralize, slugify
from django.utils.translation import gettext, get_language, activate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
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
    advice_fiscal_year = serializers.StringRelatedField()
    client = serializers.StringRelatedField()
    office = serializers.StringRelatedField()

    review = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    status_display_html = serializers.SerializerMethodField()
    multiregional_display = serializers.SerializerMethodField()
    issue_html = serializers.SerializerMethodField()
    rationale_html = serializers.SerializerMethodField()
    advice_needed_by_display = serializers.SerializerMethodField()
    prioritization_display = serializers.SerializerMethodField()
    submission_date_display = serializers.SerializerMethodField()
    language_display = serializers.SerializerMethodField()
    section_display = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    funding_display = serializers.SerializerMethodField()
    risk_text_html = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    has_process = serializers.SerializerMethodField()
    is_rescheduled = serializers.SerializerMethodField()
    is_valid_request = serializers.SerializerMethodField()
    prioritization_display_short = serializers.SerializerMethodField()
    coordinator = serializers.SerializerMethodField()
    tags_display = serializers.SerializerMethodField()

    def get_tags_display(self, instance):
        if instance.tags.exists():
            return listrify(instance.tags.all())

    def get_coordinator(self, instance):
        return str(instance.office.coordinator)

    def get_prioritization_display_short(self, instance):
        return instance.get_prioritization_display()

    def get_is_valid_request(self, instance):
        return instance.is_valid_request

    def get_is_rescheduled(self, instance):
        return instance.is_rescheduled

    def get_has_process(self, instance):
        return instance.has_process

    def get_region(self, instance):
        return instance.region

    def get_is_complete(self, instance):
        return instance.is_complete

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

    def get_issue_html(self, instance):
        return instance.issue_html

    def get_multiregional_display(self, instance):
        return instance.multiregional_display

    def get_status_display_html(self, instance):
        return f'<span class=" px-1 py-1 {instance.status_class}">{instance.get_status_display()}</span>'

    def get_status_display(self, instance):
        return instance.get_status_display()

    def get_review(self, instance):
        if hasattr(instance, "review"):
            return CSASRequestReviewSerializer(instance.review).data


class CSASRequestReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CSASRequestReview
        fields = "__all__"

    advice_date_display = serializers.SerializerMethodField()
    decision_date_display = serializers.SerializerMethodField()
    last_modified_string = serializers.SerializerMethodField()
    decision_display = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    is_valid_display = serializers.SerializerMethodField()
    is_feasible_display = serializers.SerializerMethodField()
    email_notification_date_display = serializers.SerializerMethodField()

    def get_email_notification_date_display(self, instance):
        if instance.email_notification_date:
            return date(instance.email_notification_date)

    def get_is_valid_display(self, instance):
        return instance.get_is_valid_display()

    def get_is_feasible_display(self, instance):
        return instance.get_is_feasible_display()

    def get_metadata(self, instance):
        return instance.metadata

    def get_decision_display(self, instance):
        return instance.decision_display

    def get_last_modified_string(self, instance):
        return instance.last_modified_string

    def get_advice_date_display(self, instance):
        if instance.advice_date:
            return instance.advice_date.strftime("%Y-%m-%d")

    def get_decision_date_display(self, instance):
        if instance.decision_date:
            return instance.decision_date.strftime("%Y-%m-%d")

    def validate(self, attrs):
        """
            if there is already a process, the decision must be screened in.
        """
        decision = attrs.get("decision")
        if self.instance and self.instance.csas_request.processes.exists() and decision != 1:
            msg = gettext('The review recommendation must be screened-in if there is already a CSAS Process underway.')
            raise ValidationError(msg)
        return attrs


class MeetingSerializerLITE(serializers.ModelSerializer):
    class Meta:
        model = models.Meeting
        exclude = ["updated_at", "created_at"]  # "slug", 'author'

    display = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    display_dates = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    start_date_display = serializers.SerializerMethodField()

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

    def get_display_dates(self, instance):
        start = date(instance.start_date) if instance.start_date else "??"
        dates = f'{start}'
        if instance.end_date and instance.end_date != instance.start_date:
            end = date(instance.end_date)
            dates += f' &rarr; {end}'
        days_display = "{} {}{}".format(instance.length_days, gettext("day"), pluralize(instance.length_days))
        dates += f' ({days_display})'
        return dates


class DocumentSerializerLITE(serializers.ModelSerializer):
    document_type = serializers.StringRelatedField()

    class Meta:
        model = models.Document
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    document_type = serializers.StringRelatedField()
    ttitle = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    process = serializers.StringRelatedField()
    metadata = serializers.SerializerMethodField()
    tracking = serializers.SerializerMethodField()
    file_en_size = serializers.SerializerMethodField()
    tstatus_display = serializers.SerializerMethodField()
    tstatus_text = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()
    coordinator = serializers.SerializerMethodField()
    pub_number_request_date_display = serializers.SerializerMethodField()
    due_date_display = serializers.SerializerMethodField()
    can_confirm = serializers.SerializerMethodField()

    def get_can_confirm(self, instance):
        return instance.can_confirm

    def get_due_date_display(self, instance):
        if instance.due_date:
            return f"{date(instance.due_date)} ({naturaltime(instance.due_date)})"

    def get_pub_number_request_date_display(self, instance):
        if instance.pub_number_request_date:
            return f"{date(instance.pub_number_request_date)} ({naturaltime(instance.pub_number_request_date)})"

    def get_coordinator(self, instance):
        return str(instance.process.coordinator)

    def get_status_text(self, instance):
        return instance.get_status_display()

    def get_tstatus_text(self, instance):
        return instance.get_translation_status_display()

    def get_tstatus_display(self, instance):
        return instance.tstatus_display

    def get_file_en_size(self, instance):
        if instance.file_en.name:
            return f"{round((instance.file_en.size / 1000), 3)} kb"

    def get_tracking(self, instance):
        if hasattr(instance, "tracking"):
            return DocumentTrackingSerializer(instance.tracking).data

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

    date_division_manager_sent_display = serializers.SerializerMethodField()

    def get_date_division_manager_sent_display(self, instance):
        if instance.date_division_manager_sent:
            return instance.date_division_manager_sent.strftime("%Y-%m-%d")

    date_division_manager_appr_display = serializers.SerializerMethodField()

    def get_date_division_manager_appr_display(self, instance):
        if instance.date_division_manager_appr:
            return instance.date_division_manager_appr.strftime("%Y-%m-%d")

    date_section_head_sent_display = serializers.SerializerMethodField()

    def get_date_section_head_sent_display(self, instance):
        if instance.date_section_head_sent:
            return instance.date_section_head_sent.strftime("%Y-%m-%d")

    date_section_head_appr_display = serializers.SerializerMethodField()

    def get_date_section_head_appr_display(self, instance):
        if instance.date_section_head_appr:
            return instance.date_section_head_appr.strftime("%Y-%m-%d")

    date_director_sent_display = serializers.SerializerMethodField()

    def get_date_director_sent_display(self, instance):
        if instance.date_director_sent:
            return instance.date_director_sent.strftime("%Y-%m-%d")

    date_director_appr_display = serializers.SerializerMethodField()

    def get_date_director_appr_display(self, instance):
        if instance.date_director_appr:
            return instance.date_director_appr.strftime("%Y-%m-%d")

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

    translation_review_date_display = serializers.SerializerMethodField()

    def get_translation_review_date_display(self, instance):
        if instance.translation_review_date:
            return instance.translation_review_date.strftime("%Y-%m-%d")

    anticipated_return_date_display = serializers.SerializerMethodField()

    def get_anticipated_return_date_display(self, instance):
        if instance.anticipated_return_date:
            return instance.anticipated_return_date.strftime("%Y-%m-%d")

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
    metadata = serializers.SerializerMethodField()
    display_dates = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    start_date_display = serializers.SerializerMethodField()
    attendees = serializers.SerializerMethodField()
    length_days = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()
    somp_notification_date = serializers.SerializerMethodField()
    ttime = serializers.SerializerMethodField()
    email_list = serializers.SerializerMethodField()
    process_object = serializers.SerializerMethodField()
    mmmmyy = serializers.SerializerMethodField()
    expected_publications_en = serializers.SerializerMethodField()
    key_invitees = serializers.SerializerMethodField()
    posting_status = serializers.SerializerMethodField()
    can_post_meeting = serializers.SerializerMethodField()
    posting_request_date_display = serializers.SerializerMethodField()
    posting_notification_date_display = serializers.SerializerMethodField()
    media_display = serializers.SerializerMethodField()
    can_submit_somp = serializers.SerializerMethodField()
    chair_comments_html = serializers.SerializerMethodField()

    def get_chair_comments_html(self, instance):
        return instance.chair_comments_html

    def get_can_submit_somp(self, instance):
        return instance.can_submit_somp

    def get_media_display(self, instance):
        return instance.media_display

    def get_posting_notification_date_display(self, instance):
        if instance.posting_notification_date:
            return f"{date(instance.posting_notification_date)} ({naturaltime(instance.posting_notification_date)})"

    def get_posting_request_date_display(self, instance):
        if instance.posting_request_date:
            return f"{date(instance.posting_request_date)} ({naturaltime(instance.posting_request_date)})"

    def get_can_post_meeting(self, instance):
        return instance.can_post_meeting

    def get_posting_status(self, instance):
        return instance.posting_status

    def get_key_invitees(self, instance):
        return InviteeSerializerLITE(instance.key_invitees, many=True).data

    def get_expected_publications_en(self, instance):
        return instance.expected_publications_en

    def get_mmmmyy(self, instance):
        return instance.mmmmyy

    def get_process_object(self, instance):
        return ProcessSerializerLITE(instance.process).data

    def get_email_list(self, instance):
        return instance.email_list

    def get_ttime(self, instance):
        return instance.ttime

    def get_somp_notification_date(self, instance):
        return date(instance.somp_notification_date)

    def get_display(self, instance):
        return instance.display

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

    def get_created_at_display(self, instance):
        return date(instance.created_at)


class MeetingNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MeetingNote
        fields = "__all__"

    type_display = serializers.SerializerMethodField()
    last_modified = serializers.SerializerMethodField()

    meeting_display = serializers.SerializerMethodField()

    def get_meeting_display(self, instance):
        return str(instance.meeting)

    def get_last_modified(self, instance):
        return instance.last_modified

    def get_type_display(self, instance):
        return instance.get_type_display()


class ProcessNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProcessNote
        fields = "__all__"

    type_display = serializers.SerializerMethodField()
    last_modified = serializers.SerializerMethodField()

    process_display = serializers.SerializerMethodField()

    def get_process_display(self, instance):
        return str(instance.process)

    def get_last_modified(self, instance):
        return instance.last_modified

    def get_type_display(self, instance):
        return instance.get_type_display()


class DocumentNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentNote
        fields = "__all__"

    type_display = serializers.SerializerMethodField()
    last_modified = serializers.SerializerMethodField()
    document_display = serializers.SerializerMethodField()

    def get_document_display(self, instance):
        return str(instance.document)

    def get_last_modified(self, instance):
        return instance.last_modified

    def get_type_display(self, instance):
        return instance.get_type_display()


class CSASRequestNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CSASRequestNote
        fields = "__all__"

    request_display = serializers.SerializerMethodField()

    def get_request_display(self, instance):
        return str(instance.csas_request)

    type_display = serializers.SerializerMethodField()
    last_modified = serializers.SerializerMethodField()

    def get_last_modified(self, instance):
        return instance.last_modified

    def get_type_display(self, instance):
        return instance.get_type_display()


class ProcessCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProcessCost
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


class InviteeSerializerLITE(serializers.ModelSerializer):
    class Meta:
        model = models.Invitee
        fields = "__all__"

    person_object = serializers.SerializerMethodField()
    roles_display = serializers.SerializerMethodField()

    def get_person_object(self, instance):
        return PersonSerializer(instance.person).data

    def get_roles_display(self, instance):
        if instance.roles.exists():
            return listrify(instance.roles.all())


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
    region_display = serializers.SerializerMethodField()

    def get_region_display(self, instance):
        if instance.region:
            return str(instance.region)

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


class ToRSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TermsOfReference
        fields = "__all__"

    meeting_obj = serializers.SerializerMethodField()
    expected_publications_en = serializers.SerializerMethodField()
    expected_publications_fr = serializers.SerializerMethodField()
    posting_request_date_display = serializers.SerializerMethodField()
    posting_notification_date_display = serializers.SerializerMethodField()

    def get_posting_request_date_display(self, instance):
        if instance.posting_request_date:
            return f"{date(instance.posting_request_date)} ({naturaltime(instance.posting_request_date)})"

    def get_posting_notification_date_display(self, instance):
        if instance.posting_notification_date:
            return f"{date(instance.posting_notification_date)} ({naturaltime(instance.posting_notification_date)})"

    def get_expected_publications_fr(self, instance):
        return instance.expected_publications_fr

    def get_expected_publications_en(self, instance):
        return instance.expected_publications_en

    def get_meeting_obj(self, instance):
        if instance.meeting:
            return MeetingSerializer(instance.meeting).data
        return {}


class ToRReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ToRReviewer
        fields = "__all__"

    comments_html = serializers.SerializerMethodField()
    decision_display = serializers.SerializerMethodField()
    decision_date_display = serializers.SerializerMethodField()
    decision_date_annotation = serializers.SerializerMethodField()
    status_class = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    user_display = serializers.SerializerMethodField()
    can_be_modified = serializers.SerializerMethodField()
    review_duration = serializers.SerializerMethodField()

    role_display = serializers.SerializerMethodField()

    def get_review_duration(self, instance):
        return instance.review_duration

    def get_can_be_modified(self, instance):
        return instance.can_be_modified

    def get_decision_date_annotation(self, instance):
        return naturaltime(instance.decision_date)

    def get_comments_html(self, instance):
        return instance.comments_html

    def get_decision_display(self, instance):
        return instance.get_decision_display()

    def get_status_class(self, instance):
        lang = get_language()
        activate("en")
        mystr = slugify(instance.get_status_display())
        activate(lang)
        return mystr

    def get_decision_date_display(self, instance):
        return date(instance.decision_date)

    def get_status_display(self, instance):
        return instance.get_status_display()

    def get_role_display(self, instance):
        return instance.get_role_display()

    def get_user_display(self, instance):
        return instance.user.get_full_name() if instance.user else None

    def validate(self, attrs):

        if self.instance:
            tor = self.instance.tor
            role = attrs.get("role")
            # if trying to change to reviewer, and there is a submission date and there are no other approvers, that's a problem..
            if role == 2 and tor.submission_date and not tor.reviewers.filter(~Q(id=self.instance.id)).filter(role=1).exists():
                msg = gettext('There has to be at least one approver in the queue!')
                raise ValidationError(msg)
        return attrs



class RequestReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RequestReviewer
        fields = "__all__"

    comments_html = serializers.SerializerMethodField()
    decision_display = serializers.SerializerMethodField()
    decision_date_display = serializers.SerializerMethodField()
    decision_date_annotation = serializers.SerializerMethodField()
    status_class = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    user_display = serializers.SerializerMethodField()
    can_be_modified = serializers.SerializerMethodField()
    review_duration = serializers.SerializerMethodField()

    role_display = serializers.SerializerMethodField()

    def get_role_display(self, instance):
        return instance.get_role_display()

    def get_review_duration(self, instance):
        return instance.review_duration

    def get_can_be_modified(self, instance):
        return instance.can_be_modified

    def get_decision_date_annotation(self, instance):
        return naturaltime(instance.decision_date)

    def get_comments_html(self, instance):
        return instance.comments_html

    def get_decision_display(self, instance):
        return instance.get_decision_display()

    def get_status_class(self, instance):
        lang = get_language()
        activate("en")
        mystr = slugify(instance.get_status_display())
        activate(lang)
        return mystr

    def get_decision_date_display(self, instance):
        return date(instance.decision_date)

    def get_status_display(self, instance):
        return instance.get_status_display()

    def get_user_display(self, instance):
        return instance.user.get_full_name() if instance.user else None

    def validate(self, attrs):
        if self.instance:
            csas_request = self.instance.csas_request
            role = attrs.get("role")
            # if trying to change to reviewer, and there is a submission date and there are no other approvers, that's a problem..
            if role == 2 and csas_request.submission_date and not csas_request.reviewers.filter(~Q(id=self.instance.id)).filter(role=1).exists():
                msg = gettext('There has to be at least one approver in the queue!')
                raise ValidationError(msg)
        return attrs


class ProcessSerializerLITE(serializers.ModelSerializer):
    fiscal_year = serializers.StringRelatedField()
    tname = serializers.SerializerMethodField()
    scope_type = serializers.SerializerMethodField()
    regions = serializers.SerializerMethodField()
    tor = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    has_tor = serializers.SerializerMethodField()

    def get_has_tor(self, instance):
        return instance.has_tor

    def get_documents(self, instance):
        return DocumentSerializerLITE(instance.documents.all(), many=True).data

    def get_tor(self, instance):
        if hasattr(instance, "tor"):
            return instance.tor.id

    def get_regions(self, instance):
        return instance.regions

    def get_scope_type(self, instance):
        return instance.scope_type

    def get_tname(self, instance):
        return instance.tname

    class Meta:
        model = models.Process
        fields = "__all__"


class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Process
        fields = "__all__"

    editors = serializers.SerializerMethodField()
    chair = serializers.SerializerMethodField()
    lead_office = serializers.StringRelatedField()
    fiscal_year = serializers.StringRelatedField()
    has_tor = serializers.SerializerMethodField()
    has_tor_meeting = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    other_offices = serializers.SerializerMethodField()
    scope_type = serializers.SerializerMethodField()
    tname = serializers.SerializerMethodField()
    client_sectors = serializers.SerializerMethodField()
    science_leads = serializers.SerializerMethodField()
    client_leads = serializers.SerializerMethodField()
    committee_members = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    status_display_html = serializers.SerializerMethodField()
    regions = serializers.SerializerMethodField()
    advice_date_display = serializers.SerializerMethodField()
    can_post_meeting = serializers.SerializerMethodField()
    key_meetings = serializers.SerializerMethodField()
    tor = serializers.SerializerMethodField()
    tor_status = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    def get_projects(self, instance):
        from ppt.api.serializers import ProjectSerializer
        return [ProjectSerializer(p).data for p in instance.projects.all()]

    def get_tor_status(self, instance):
        return instance.tor_status

    def get_tor(self, instance):
        if hasattr(instance, "tor"):
            return ToRSerializer(instance.tor).data

    def get_key_meetings(self, instance):
        return MeetingSerializerLITE(instance.meetings.filter(is_planning=False), many=True, read_only=True).data

    def get_can_post_meeting(self, instance):
        pass

    def get_advice_date_display(self, instance):
        return date(instance.advice_date)

    def get_committee_members(self, instance):
        return instance.committee_members

    def get_client_leads(self, instance):
        return instance.client_leads

    def get_science_leads(self, instance):
        return instance.science_leads

    def get_client_sectors(self, instance):
        return instance.client_sectors

    def get_editors(self, instance):
        return listrify(instance.editors.all())

    def get_chair(self, instance):
        return instance.chair

    def get_has_tor(self, instance):
        return instance.has_tor

    def get_has_tor_meeting(self, instance):
        return instance.has_tor and instance.tor.meeting is not None

    def get_metadata(self, instance):
        return instance.metadata

    def get_other_offices(self, instance):
        return listrify(instance.other_offices.all())

    def get_scope_type(self, instance):
        return instance.scope_type

    def get_tname(self, instance):
        return instance.tname

    def get_status_display(self, instance):
        return instance.get_status_display()

    def get_status_display_html(self, instance):
        return f'<span class=" px-1 py-1 {instance.status_class}">{instance.get_status_display()}</span>'

    def get_regions(self, instance):
        return str(instance.regions)
