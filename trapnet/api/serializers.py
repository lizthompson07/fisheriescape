from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Species
        fields = "__all__"


class SpecimenSerializer(serializers.ModelSerializer):
    species_object = serializers.SerializerMethodField()
    species_display = serializers.SerializerMethodField()
    sex_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    life_stage_display = serializers.SerializerMethodField()
    reproductive_status_display = serializers.SerializerMethodField()
    adipose_condition_display = serializers.SerializerMethodField()

    def get_adipose_condition_display(self, instance):
        return instance.get_adipose_condition_display()

    def get_reproductive_status_display(self, instance):
        return str(instance.reproductive_status) if instance.reproductive_status else None

    def get_life_stage_display(self, instance):
        return str(instance.life_stage) if instance.life_stage else None

    def get_status_display(self, instance):
        return str(instance.status) if instance.status else None

    def get_sex_display(self, instance):
        return str(instance.sex) if instance.sex else None

    def get_species_display(self, instance):
        return str(instance.species)

    def get_species_object(self, instance):
        return SpeciesSerializer(instance.species).data

    class Meta:
        model = models.Specimen
        fields = "__all__"

    def validate(self, attrs):
        """
        form validation:
        - make sure there is at least a sample or a sweep!
        """
        sample = attrs.get("sample")
        sweep = attrs.get("sweep")
        if not sample and not sweep:
            msg = _('You must supply either a sample or a sweep!')
            raise ValidationError(msg)

        return attrs


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sample
        fields = "__all__"

class EFSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EFSample
        fields = "__all__"

