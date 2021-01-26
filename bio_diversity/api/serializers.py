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


class IndividualDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Individual
        fields = "__all__"

    stok = serializers.SerializerMethodField()
    coll = serializers.SerializerMethodField()
    spec = serializers.SerializerMethodField()
    grp = serializers.SerializerMethodField()

    def get_stok(self, instance):
        return instance.stok_id.__str__()

    def get_coll(self, instance):
        return instance.coll_id.__str__()

    def get_spec(self, instance):
        return instance.spec_id.__str__()

    def get_grp(self, instance):
        return instance.grp_id.__str__()

