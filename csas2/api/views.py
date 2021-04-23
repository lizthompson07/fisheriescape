from datetime import datetime

from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared_models.api.serializers import PersonSerializer
from shared_models.api.views import _get_labels
from shared_models.models import Person, Language
from . import serializers
from .permissions import CanModifyRequestOrReadOnly, CanModifyProcessOrReadOnly
from .. import models, emails, model_choices


# USER
#######
class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        return Response(data)


class CSASRequestViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CSASRequestSerializer
    permission_classes = [CanModifyRequestOrReadOnly]
    queryset = models.CSASRequest.objects.all()


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = models.Meeting.objects.all().order_by("-created_at")
    serializer_class = serializers.MeetingSerializer
    permission_classes = [CanModifyProcessOrReadOnly]

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("process"):
            process = get_object_or_404(models.Process, pk=qp.get("process"))
            qs = process.meetings.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
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
        raise ValidationError(_("You need to specify a meeting"))

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class InviteeViewSet(viewsets.ModelViewSet):
    queryset = models.Invitee.objects.all()
    serializer_class = serializers.InviteeSerializer
    permission_classes = [CanModifyProcessOrReadOnly]

    # pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        obj = serializer.save(updated_by=self.request.user)

        # it is important to use the try/except approach because this way
        # it can differentiate between  1) no dates value being passed or 2) a null value (i.e. clear all attendance)
        try:
            dates = self.request.data["dates"]
        except KeyError:
            pass
        else:
            # delete any existing attendance
            obj.attendance.all().delete()
            for date in dates.split(", "):
                dt = datetime.strptime(date.strip(), "%Y-%m-%d")
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
                models.Attendance.objects.create(invitee=obj, date=dt)

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
        raise ValidationError(_("This endpoint cannot be used without a query param"))


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


class NoteModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.MeetingNote

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['type_choices'] = [dict(text=c[1], value=c[0]) for c in model_choices.meeting_note_type_choices]
        return Response(data)


class InviteeModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Invitee

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['person_choices'] = [dict(text=str(p), value=p.id) for p in Person.objects.all()]
        data['status_choices'] = [dict(text=c[1], value=c[0]) for c in model_choices.invitee_status_choices]
        data['role_choices'] = [dict(text=c[1], value=c[0]) for c in model_choices.invitee_role_choices]
        return Response(data)


class PersonModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = Person

    def get(self, request):
        data = dict()
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
