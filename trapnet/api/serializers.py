from django.contrib.auth.models import User
from rest_framework import serializers

from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Species
        fields = "__all__"


class ObservationSerializer(serializers.ModelSerializer):
    species_object = serializers.SerializerMethodField()
    species_display = serializers.SerializerMethodField()
    sex_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    origin_display = serializers.SerializerMethodField()
    date_tagged_display = serializers.SerializerMethodField()

    def get_date_tagged_display(self, instance):
        if instance.date_tagged:
            return instance.date_tagged.strftime("%Y-%m-%d")

    def get_origin_display(self, instance):
        return str(instance.origin) if instance.origin else None

    def get_status_display(self, instance):
        return str(instance.status) if instance.status else None

    def get_sex_display(self, instance):
        return str(instance.sex) if instance.sex else None

    def get_species_display(self, instance):
        return str(instance.species)

    def get_species_object(self, instance):
        return SpeciesSerializer(instance.species).data

    class Meta:
        model = models.Observation
        fields = "__all__"
