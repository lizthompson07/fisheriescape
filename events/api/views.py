from datetime import datetime

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dm_apps.utils import custom_send_mail
from shared_models.utils import special_capitalize
from . import serializers
# USER
#######
from .pagination import StandardResultsSetPagination
from .. import models, emails


def _get_labels(model):
    labels = {}
    for field in model._meta.get_fields():
        if hasattr(field, "name") and hasattr(field, "verbose_name"):
            labels[field.name] = special_capitalize(field.verbose_name)
    return labels


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        return Response(data)


class EventModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Event

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['type_choices'] = [dict(text=c[1], value=c[0]) for c in self.model.type_choices]
        event_choices = [dict(text=obj.tname, value=obj.id) for obj in self.model.objects.all()]
        event_choices.insert(0, dict(text="------", value=None))
        data['event_choices'] = event_choices
        return Response(data)


class NoteModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Note

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['type_choices'] = [dict(text=c[1], value=c[0]) for c in self.model.type_choices]
        return Response(data)


class InviteeModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Invitee

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['status_choices'] = [dict(text=c[1], value=c[0]) for c in self.model.status_choices]
        data['role_choices'] = [dict(text=c[1], value=c[0]) for c in self.model.role_choices]
        return Response(data)


class ResourceModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Resource

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        return Response(data)


class EventViewSet(viewsets.ModelViewSet):
    queryset = models.Event.objects.all().order_by("-created_at")
    # lookup_field = 'slug'
    serializer_class = serializers.EventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        parent_event = serializer.validated_data.get("parent_event")
        if parent_event == serializer.instance:
            raise ValidationError("An event cannot be it's own parent, silly. ")

        serializer.save()


class NoteViewSet(viewsets.ModelViewSet):
    queryset = models.Note.objects.all()
    # lookup_field = 'slug'
    serializer_class = serializers.NoteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        qs = self.queryset
        if self.request.query_params.get("event"):
            qs = qs.filter(event_id=self.request.query_params.get("event"))
        return qs


class InviteeViewSet(viewsets.ModelViewSet):
    queryset = models.Invitee.objects.all()
    serializer_class = serializers.InviteeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        obj = serializer.save()

        # it is important to use the try/except approach because this way
        # it can differentiate between  1) no dates value being passed or 2) a null value (i.e. clear all attendance)
        try:
            dates = self.request.data["dates"]
        except KeyError:
            pass
        else:
            # delete any existing attendance
            obj.attendance.all().delete()
            for date in dates:
                dt = datetime.strptime(date, "%Y-%m-%d")
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
                models.Attendance.objects.create(invitee=obj, date=dt)

    def get_queryset(self):
        qs = self.queryset
        if self.request.query_params.get("event"):
            qs = qs.filter(event_id=self.request.query_params.get("event"))
        return qs


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = models.Resource.objects.all()
    serializer_class = serializers.ResourceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        resource = serializer.save(created_by=self.request.user)

        # decide on who should receive an update
        for invitee in resource.event.invitees.all():
            # only send the email to those who already received an invitation (and where this happened in the past... redundant? )
            if invitee.invitation_sent_date and invitee.invitation_sent_date < resource.created_at:
                email = emails.NewResourceEmail(invitee, resource, self.request)
                custom_send_mail(
                    subject=email.subject,
                    html_message=email.message,
                    from_email=email.from_email,
                    recipient_list=email.to_list
                )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_queryset(self):
        qs = self.queryset
        if self.request.query_params.get("event"):
            qs = qs.filter(event_id=self.request.query_params.get("event"))
        return qs


class InviteeSendInvitationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """ send the email"""
        invitee = get_object_or_404(models.Invitee, pk=pk)
        if not invitee.invitation_sent_date:
            # send email
            email = emails.InvitationEmail(invitee, request)
            custom_send_mail(
                subject=email.subject,
                html_message=email.message,
                from_email=email.from_email,
                recipient_list=email.to_list
            )
            invitee.invitation_sent_date = timezone.now()
            invitee.save()


            return Response("email sent.", status=status.HTTP_200_OK)
        return Response("An email has already been sent to this invitee.", status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        """ get a preview of the email to be sent"""
        invitee = get_object_or_404(models.Invitee, pk=pk)
        # send email
        email = emails.InvitationEmail(invitee, request)
        return Response(email.to_dict(), status=status.HTTP_200_OK)
