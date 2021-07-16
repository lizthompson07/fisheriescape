from django.contrib.auth.models import User
from rest_framework import serializers

from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class SampleSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()

    datetime_display = serializers.SerializerMethodField()

    def get_datetime_display(self, instance):
        if instance.datetime:
            return instance.datetime.strftime("%Y-%m-%d %H:%M")

    def get_display(self, instance):
        return str(instance)

    class Meta:
        model = models.Sample
        fields = "__all__"


class FilterSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()
    datetime_display = serializers.SerializerMethodField()

    def get_datetime_display(self, instance):
        if instance.start_datetime:
            return instance.start_datetime.strftime("%Y-%m-%d %H:%M")

    def get_display(self, instance):
        return str(instance)

    class Meta:
        model = models.Filter
        fields = "__all__"


class DNAExtractSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()
    datetime_display = serializers.SerializerMethodField()

    def get_datetime_display(self, instance):
        if instance.start_datetime:
            return instance.start_datetime.strftime("%Y-%m-%d %H:%M")

    def get_display(self, instance):
        return str(instance)

    class Meta:
        model = models.DNAExtract
        fields = "__all__"


class SpeciesObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SpeciesObservation
        fields = "__all__"

    species_display = serializers.SerializerMethodField()

    def get_species_display(self, instance):
        return str(instance.species)


class PCRSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PCR
        fields = "__all__"

    pcr_number = serializers.SerializerMethodField()
    observations = SpeciesObservationSerializer(many=True, read_only=True)
    display = serializers.SerializerMethodField()
    datetime_display = serializers.SerializerMethodField()

    def get_datetime_display(self, instance):
        if instance.start_datetime:
            return instance.start_datetime.strftime("%Y-%m-%d %H:%M")

    def get_display(self, instance):
        return str(instance)

    def get_pcr_number(self, instance):
        return instance.pcr_number
