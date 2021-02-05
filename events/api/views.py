from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from masterlist.models import Person
from shared_models.utils import special_capitalize
from . import serializers
# USER
#######
from .pagination import StandardResultsSetPagination
from .. import models


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


class EventViewSet(viewsets.ModelViewSet):
    queryset = models.Event.objects.all().order_by("-created_at")
    # lookup_field = 'slug'
    serializer_class = serializers.EventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


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


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = serializers.PersonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email_1', 'email_2']

    def perform_create(self, serializer):
        serializer.save(last_modified_by=self.request.user)

    # def get_queryset(self):
    #     qs = self.queryset
    #     if self.request.query_params.get("event"):
    #         qs = qs.filter(event_id=self.request.query_params.get("event"))
    #     return qs


class InviteeViewSet(viewsets.ModelViewSet):
    queryset = models.Invitee.objects.all()
    serializer_class = serializers.InviteeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        qs = self.queryset
        if self.request.query_params.get("event"):
            qs = qs.filter(event_id=self.request.query_params.get("event"))
        return qs
#
