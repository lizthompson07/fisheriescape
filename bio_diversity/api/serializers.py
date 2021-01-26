from django.contrib.auth.models import User
from django.template.defaultfilters import date
from markdown import markdown
from rest_framework import serializers

from lib.functions.custom_functions import listrify
from shared_models import models as shared_models
from .. import models
from ..utils import bio_diverisity_admin


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "is_admin"]

    is_admin = serializers.SerializerMethodField()

    def get_is_admin(self, instance):
        return bio_diverisity_admin(instance)

