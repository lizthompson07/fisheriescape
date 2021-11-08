from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from unidecode import unidecode

from shared_models.api.serializers import PersonSerializer
from shared_models.api.views import _get_labels
from shared_models.models import Person, Language, Region, FiscalYear
from . import serializers
from .pagination import StandardResultsSetPagination
from .permissions import CanModifyRequestOrReadOnly, CanModifyProcessOrReadOnly, RequestNotesPermission
from .. import models, emails, model_choices, utils


# USER
#######
class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        qp = request.GET
        data["is_csas_national_admin"] = utils.in_csas_national_admin_group(request.user)
        data["is_admin"] = utils.in_csas_admin_group(request.user)

        # provide the region for which that use is an admin for, if applicable
        data["regional_admin"] = None
        if hasattr(request.user, "csas_admin_user"):
            data["regional_admin"] = request.user.csas_admin_user.region_id

        if qp.get("request"):
            data["can_modify"] = utils.can_modify_request(request.user, qp.get("request"), return_as_dict=True)
        elif qp.get("process"):
            data["can_modify"] = utils.can_modify_process(request.user, qp.get("process"), return_as_dict=True)
        elif qp.get("document"):
            doc = get_object_or_404(models.Document, pk=qp.get("document"))
            data["can_modify"] = utils.can_modify_process(request.user, doc.process_id, return_as_dict=True)
        elif qp.get("meeting"):
            meeting = get_object_or_404(models.Meeting, pk=qp.get("meeting"))
            data["can_modify"] = utils.can_modify_process(request.user, meeting.process_id, return_as_dict=True)
        return Response(data)


class CSASRequestViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CSASRequestSerializer
    permission_classes = [CanModifyRequestOrReadOnly]
    queryset = models.CSASRequest.objects.all()
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['id', 'title', 'translated_title']
    filterset_fields = [
        'section__division__branch__sector__region',
        "section__division__branch__sector",
        "section__division__branch",
        "section__division",
        "section",
        "fiscal_year",
        "status",
        "review__decision",
    ]


class CSASRequestNoteViewSet(viewsets.ModelViewSet):
    queryset = models.CSASRequestNote.objects.all()
    serializer_class = serializers.CSASRequestNoteSerializer
    permission_classes = [RequestNotesPermission]

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("csas_request"):
            csas_request = get_object_or_404(models.CSASRequest, pk=qp.get("csas_request"))
            qs = csas_request.notes.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        elif qp.get("user"):
            user = get_object_or_404(User, pk=qp.get("user"))
            qs = user.csasrequestnote_created_by.filter(type=2, is_complete=False)
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        raise ValidationError(_("You need to specify at least one query param."))

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class CSASRequestReviewViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CSASRequestReviewSerializer
    permission_classes = [CanModifyRequestOrReadOnly]
    queryset = models.CSASRequestReview.objects.all()

    def perform_destroy(self, instance):
        # a little bit of gymnastics here in order to save the csas request truely following the deletion of the review (not working with signals)
        csas_request = instance.csas_request
        instance.delete()
        csas_request.save()


class ProcessViewSet(viewsets.ModelViewSet):
    queryset = models.Process.objects.all().order_by("-created_at")
    serializer_class = serializers.ProcessSerializer
    permission_classes = [CanModifyProcessOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['id', 'name', 'nom']
    filterset_fields = [
        'fiscal_year',
        'id',
        'lead_region',
        "is_posted"
    ]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        kwargs = dict(updated_by=self.request.user)
        obj = serializer.save(**kwargs)
        # we do not want to send them too many emails.. only the first time
        if obj.is_posted and not obj.posting_notification_date:
            email = emails.PostedProcessEmail(self.request, obj)
            email.send()
            obj.posting_notification_date = timezone.now()
            obj.save()

    def post(self, request, pk):
        qp = request.query_params
        process = get_object_or_404(models.Process, pk=pk)
        if qp.get("request_posting"):
            if not process.is_posted:
                email = emails.PostingRequestEmail(request, process)
                email.send()
                process.posting_request_date = timezone.now()
                process.save()
                msg = _("Success! Your request for a posting has been sent to the National CSAS Office.")
                return Response(msg, status.HTTP_200_OK)
            raise ValidationError(_("A request to have this process posted has already occurred."))
        raise ValidationError(_("This endpoint cannot be used without a query param"))


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = models.Meeting.objects.all().order_by("-created_at")
    serializer_class = serializers.MeetingSerializer
    permission_classes = [CanModifyProcessOrReadOnly]

    def post(self, request, pk):
        qp = request.query_params
        meeting = get_object_or_404(models.Meeting, pk=pk)
        if qp.get("maximize_attendance"):
            invitees = meeting.invitees.filter(status__in=[1, ])
            for invitee in invitees:
                invitee.maximize_attendance()
            return Response(None, status.HTTP_204_NO_CONTENT)
        elif qp.get("import_from_meeting"):
            target_meeting = get_object_or_404(models.Meeting, pk=qp.get("import_from_meeting"))
            invitees = target_meeting.invitees.all()
            for new_invitee in invitees:
                if not meeting.invitees.filter(person=new_invitee.person).exists():
                    i = models.Invitee.objects.create(
                        meeting=meeting,
                        person=new_invitee.person,
                        region=new_invitee.region,
                    )
                    for role in new_invitee.roles.all():
                        i.roles.add(role)
            return Response(None, status.HTTP_204_NO_CONTENT)
        raise ValidationError(_("This endpoint cannot be used without a query param"))

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("process"):
            process = get_object_or_404(models.Process, pk=qp.get("process"))
            qs = process.meetings.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        if qp.get("choices"):
            qs = models.Meeting.objects.filter(is_planning=False, invitees__isnull=False).distinct().order_by("process__lead_region", "fiscal_year")
            meeting_choices = [dict(text=m.full_display, value=m.id) for m in qs]
            meeting_choices.insert(0, dict(text="-----", value=None))
            return Response(meeting_choices)
        raise ValidationError(_("You need to specify a csas process"))

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class MeetingNoteViewSet(viewsets.ModelViewSet):
    queryset = models.MeetingNote.objects.all()
    serializer_class = serializers.MeetingNoteSerializer
    permission_classes = [CanModifyProcessOrReadOnly]

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("meeting"):
            meeting = get_object_or_404(models.Meeting, pk=qp.get("meeting"))
            qs = meeting.notes.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        elif qp.get("user"):
            user = get_object_or_404(User, pk=qp.get("user"))
            qs = user.meetingnote_created_by.filter(type=2, is_complete=False)
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        raise ValidationError(_("You need to specify a meeting"))

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class ProcessNoteViewSet(viewsets.ModelViewSet):
    queryset = models.ProcessNote.objects.all()
    serializer_class = serializers.ProcessNoteSerializer
    permission_classes = [CanModifyProcessOrReadOnly]

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("process"):
            process = get_object_or_404(models.Process, pk=qp.get("process"))
            qs = process.notes.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        elif qp.get("user"):
            user = get_object_or_404(User, pk=qp.get("user"))
            qs = user.processnote_created_by.filter(type=2, is_complete=False)
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        raise ValidationError(_("You need to specify a process"))

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class ProcessCostViewSet(viewsets.ModelViewSet):
    queryset = models.ProcessCost.objects.all()
    serializer_class = serializers.ProcessCostSerializer
    permission_classes = [CanModifyProcessOrReadOnly]

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("process"):
            process = get_object_or_404(models.Process, pk=qp.get("process"))
            qs = process.costs.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        raise ValidationError(_("You need to specify a process"))

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class InviteeViewSet(viewsets.ModelViewSet):
    queryset = models.Invitee.objects.all()
    serializer_class = serializers.InviteeSerializer
    permission_classes = [CanModifyProcessOrReadOnly]

    # pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        meeting = get_object_or_404(models.Meeting, pk=self.request.data.get("meeting"))
        old_chair = meeting.chair
        serializer.save()
        new_chair = meeting.chair

        # now for the piece about NCR email
        if meeting.process.is_posted and hasattr(meeting, "tor") and (old_chair != new_chair):
            email = emails.UpdatedMeetingEmail(self.request, meeting, old_chair=old_chair, new_chair=new_chair)
            email.send()

    def perform_update(self, serializer):
        meeting = get_object_or_404(models.Invitee, pk=self.kwargs.get("pk")).meeting
        old_chair = meeting.chair
        obj = serializer.save()
        new_chair = meeting.chair

        # now for the piece about NCR email
        if meeting.process.is_posted and hasattr(meeting, "tor") and (old_chair != new_chair):
            email = emails.UpdatedMeetingEmail(self.request, meeting, old_chair=old_chair, new_chair=new_chair)
            email.send()

        # it is important to use the try/except approach because this way
        # it can differentiate between  1) no dates value being passed or 2) a null value (i.e. clear all attendance)
        try:
            dates = self.request.data["dates"]
        except KeyError:
            pass
        else:
            try:
                # delete any existing attendance
                obj.attendance.all().delete()
                for date in dates.split(", "):
                    dt = datetime.strptime(date.strip(), "%Y-%m-%d")
                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
                    models.Attendance.objects.create(invitee=obj, date=dt)
            except:
                pass

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("meeting"):
            meeting = get_object_or_404(models.Meeting, pk=qp.get("meeting"))
            qs = meeting.invitees.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        raise ValidationError(_("You need to specify a meeting"))


class MeetingResourceViewSet(viewsets.ModelViewSet):
    queryset = models.MeetingResource.objects.all()
    serializer_class = serializers.MeetingResourceSerializer
    permission_classes = [CanModifyProcessOrReadOnly]

    # pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        resource = serializer.save(created_by=self.request.user)

        # decide on who should receive an update
        for invitee in resource.meeting.invitees.all():
            # only send the email to those who already received an invitation (and where this happened in the past... redundant? )
            if invitee.invitation_sent_date and invitee.invitation_sent_date < resource.created_at:
                email = emails.NewResourceEmail(self.request, invitee, resource)
                email.send()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("meeting"):
            meeting = get_object_or_404(models.Meeting, pk=qp.get("meeting"))
            qs = meeting.resources.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        raise ValidationError(_("You need to specify a meeting"))


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer
    permission_classes = [CanModifyProcessOrReadOnly]

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("process"):
            process = get_object_or_404(models.Process, pk=qp.get("process"))
            qs = process.documents.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        raise ValidationError(_("You need to specify a csas process"))

    def post(self, request, pk):
        qp = request.query_params
        doc = get_object_or_404(models.Document, pk=pk)
        if qp.get("meeting"):
            meeting = get_object_or_404(models.Meeting, pk=qp.get("meeting"))
            if doc.meetings.filter(id=meeting.id).exists():
                doc.meetings.remove(meeting)
            else:
                doc.meetings.add(meeting)
            return Response(None, status.HTTP_204_NO_CONTENT)
        elif qp.get("request_pub_number"):
            if not doc.pub_number_request_date and not doc.pub_number:
                email = emails.PublicationNumberRequestEmail(request, doc)
                email.send()
                doc.pub_number_request_date = timezone.now()
                doc.save()
                msg = _("Success! Your request for a publication number has been sent to the National CSAS Office.")
                return Response(msg, status.HTTP_200_OK)
            raise ValidationError(_("A publication number has already been requested."))
        elif qp.get("get_pub_number"):
            if hasattr(doc, "tracking") and doc.tracking.anticipated_posting_date:
                year = doc.tracking.anticipated_posting_date.year
                p_num = "001"
                qs = models.Document.objects.filter(tracking__pub_number__startswith=year).order_by("pub_number")
                if qs.exists():
                    num_list = list()
                    for obj in qs:
                        if len(obj.pub_number.split("/")) > 1:
                            try:
                                num = int(obj.pub_number.split("/")[1])
                            except:
                                pass
                            else:
                                num_list.append(num)
                    if len(num_list):
                        num_list.sort()
                        p_num = '{:03d}'.format(num_list[-1] + 1)
                pub_number = f"{year}/{p_num}"
                return Response(dict(pub_number=pub_number), status=status.HTTP_200_OK)
            raise ValidationError(_("Cannot generate a pub number if there is no anticipated posting date."))
        elif qp.get("get_due_date"):
            # due date can be guessed based on the document type
            # but we also have to have a connected meeting!
            if not doc.document_type.days_due:
                raise ValidationError(_("Cannot guess at the due date because the document type has not pre-configuration. "
                                        "Please talk to a national CSAS administrator to have this fixed!"))
            if not doc.meetings.exists():
                raise ValidationError(_("Cannot guess at the due date because there are no connected meetings to this document!"))
            qs = doc.meetings.filter(end_date__isnull=False)
            if not qs.exists():
                raise ValidationError(_("Cannot guess at the due date because none of the connected meeting have end dates!"))
            last_date = qs.order_by("end_date").last().end_date
            return Response(dict(due_date=last_date), status=status.HTTP_200_OK)
        raise ValidationError(_("This endpoint cannot be used without a query param"))


class DocumentTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.DocumentTrackingSerializer
    # permission_classes = [CanModifyProcessOrReadOnly]
    queryset = models.DocumentTracking.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)

        # we can take a few 'best guesses'

        # is there a chair?
        chair_qs = models.Invitee.objects.filter(meeting__process=obj.document.process, roles__name__icontains=_("chair"))
        if chair_qs.exists():
            obj.chair = chair_qs.first().person

        # assume proof will be sent to lead author. But if there is no lead author, default to next in line
        author_qs = obj.document.authors.order_by("-is_lead")
        if author_qs.exists():
            obj.submitted_by = author_qs.first().person
            obj.proof_sent_to = author_qs.first().person

        obj.save()


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorSerializer
    permission_classes = [CanModifyProcessOrReadOnly]

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("document"):
            document = get_object_or_404(models.Document, pk=qp.get("document"))
            qs = document.authors.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        raise ValidationError(_("You need to specify a document"))

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class DocumentNoteViewSet(viewsets.ModelViewSet):
    queryset = models.DocumentNote.objects.all()
    serializer_class = serializers.DocumentNoteSerializer
    permission_classes = [CanModifyProcessOrReadOnly]

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("document"):
            document = get_object_or_404(models.Document, pk=qp.get("document"))
            qs = document.notes.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        elif qp.get("user"):
            user = get_object_or_404(User, pk=qp.get("user"))
            qs = user.documentnote_created_by.filter(type=2, is_complete=False)
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        raise ValidationError(_("You need to specify a document"))

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated]


# this can probably be combined into the Invitee viewset
class InviteeSendInvitationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """ send the email"""
        invitee = get_object_or_404(models.Invitee, pk=pk)
        if not invitee.invitation_sent_date:
            # send email
            email = emails.InvitationEmail(request, invitee)
            email.send()
            invitee.invitation_sent_date = timezone.now()
            invitee.save()

            return Response("email sent.", status=status.HTTP_200_OK)
        return Response("An email has already been sent to this invitee.", status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        """ get a preview of the email to be sent"""
        invitee = get_object_or_404(models.Invitee, pk=pk)
        # send email
        email = emails.InvitationEmail(request, invitee)
        return Response(email.as_dict(), status=status.HTTP_200_OK)


class MeetingModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Meeting

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        return Response(data)


class GenericNoteModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.GenericNote

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['type_choices'] = [dict(text=c[1], value=c[0]) for c in model_choices.note_type_choices]
        return Response(data)


class InviteeModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Invitee

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['status_choices'] = [dict(text=c[1], value=c[0]) for c in model_choices.invitee_status_choices]
        data['role_choices'] = [dict(text=str(obj), value=obj.id) for obj in models.InviteeRole.objects.all()]

        region_choices = [dict(text=str(obj), value=obj.id) for obj in Region.objects.all()]
        region_choices.insert(0, dict(text="-----", value=None))
        data['region_choices'] = region_choices
        return Response(data)


class PersonModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = Person

    def get(self, request):
        external_stamp = " ({})".format(_("external").upper())
        person_choices = [dict(text="{} {}".format(unidecode(str(p)), external_stamp if not p.dmapps_user else ""), value=p.id) for p in
                          Person.objects.all()]
        person_choices.insert(0, dict(text="-----", value=None))

        data = dict()
        data['person_choices'] = person_choices
        data['labels'] = _get_labels(self.model)
        data['language_choices'] = [dict(text=str(p), value=p.id) for p in Language.objects.all()]
        return Response(data)


class ResourceModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.MeetingResource

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        return Response(data)


class DocumentModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Document

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        return Response(data)


class DocumentTrackingModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.DocumentTracking

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['lang_choices'] = [dict(text=c[1], value=c[0]) for c in model_choices.language_choices]
        return Response(data)


class AuthorModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Author

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        return Response(data)


class GenericCostModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.GenericCost

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['cost_category_choices'] = [dict(text=c[1], value=c[0]) for c in model_choices.cost_category_choices]
        return Response(data)


class RequestModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.CSASRequest

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        status_choices = [dict(text=c[1], value=c[0]) for c in model_choices.request_status_choices]
        status_choices.insert(0, dict(text="-----", value=None))
        data['status_choices'] = status_choices
        data['region_choices'] = [dict(text=c[1], value=c[0]) for c in utils.get_region_choices()]
        data['sector_choices'] = [dict(text=c[1], value=c[0]) for c in utils.get_sector_choices()]
        data['fy_choices'] = [dict(text=str(c), value=c.id) for c in FiscalYear.objects.filter(csas_requests__isnull=False).distinct()]
        return Response(data)


class RequestReviewModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.CSASRequestReview

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)

        prioritization_choices = [dict(text=c[1], value=c[0]) for c in model_choices.prioritization_choices]
        prioritization_choices.insert(0, dict(text="-----", value=None))
        decision_choices = [dict(text=c[1], value=c[0]) for c in model_choices.request_decision_choices]
        decision_choices.insert(0, dict(text="-----", value=None))
        data['prioritization_choices'] = prioritization_choices
        data['decision_choices'] = decision_choices
        return Response(data)


class ProcessModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Process

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['status_choices'] = [dict(text=c[1], value=c[0]) for c in model_choices.get_process_status_choices()]
        data['region_choices'] = [dict(text=c[1], value=c[0]) for c in utils.get_region_choices()]
        data['fy_choices'] = [dict(text=str(c), value=c.id) for c in FiscalYear.objects.filter(processes__isnull=False).distinct()]

        return Response(data)
