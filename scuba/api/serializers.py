from django.contrib.auth.models import User
from django.template.defaultfilters import date
from markdown import markdown
from rest_framework import serializers

from lib.functions.custom_functions import listrify
from shared_models import models as shared_models
from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username",]

class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Observation
        fields = "__all__"

class SectionSerializer(serializers.ModelSerializer):
    observations = ObservationSerializer(many=True)
    class Meta:
        model = models.Section
        fields = "__all__"

