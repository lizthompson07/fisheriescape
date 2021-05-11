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

    stock = serializers.SerializerMethodField()
    collection = serializers.SerializerMethodField()
    species = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    length = serializers.SerializerMethodField()

    def get_stock(self, instance):
        return instance.stok_id.__str__()

    def get_length(self, instance):
        return instance.individual_detail("Length")

    def get_collection(self, instance):
        return instance.coll_id.__str__()

    def get_species(self, instance):
        return instance.spec_id.__str__()

    def get_group(self, instance):
        return instance.grp_id.__str__()


class CupDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cup
        fields = ["id", "name", "nom", "description_en", "description_fr", "drawer", "draw_id", "heath_unit",
                  "start_date", "end_date"]

    drawer = serializers.SerializerMethodField()
    heath_unit = serializers.SerializerMethodField()

    def get_drawer(self, instance):
        return instance.draw_id.__str__()

    def get_heath_unit(self, instance):
        return instance.draw_id.heat_id.__str__()


class AnixDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AniDetailXref
        fields = "__all__"


class ContxDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContainerXRef
        fields = "__all__"


class CntDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Count
        fields = "__all__"

    count_code = serializers.SerializerMethodField()

    def get_count_code(self, instance):
        return instance.cntc_id.__str__()


class GroupDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = "__all__"

    stock = serializers.SerializerMethodField()
    collection = serializers.SerializerMethodField()
    species = serializers.SerializerMethodField()

    def get_stock(self, instance):
        return instance.stok_id.__str__()

    def get_length(self, instance):
        return instance.individual_detail("Length")

    def get_collection(self, instance):
        return instance.coll_id.__str__()

    def get_species(self, instance):
        return instance.spec_id.__str__()