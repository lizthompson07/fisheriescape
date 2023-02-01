from django.contrib.auth.models import User
from rest_framework import serializers

from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "is_admin"]


class RecordDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Record
        fields = ["id", "species", "name", "source", "year", "notes", "species_name", "record_type", "geometry"]

    species_name = serializers.SerializerMethodField()
    record_type = serializers.SerializerMethodField()
    geometry = serializers.SerializerMethodField()

    def get_species_name(self, instance):
        return instance.species.full_name

    def get_record_type(self, instance):
        return instance.get_record_type_display()

    def get_geometry(self, instance):
        return instance.all_points()


class SpeciesDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Species
        fields = ["id", "common_name_eng", "common_name_fre", "population_eng", "population_fre", "scientific_name",
                  "tsn", "notes_eng", "notes_fra", "taxon", "cosewic_status", "sara_status", "ns_status",
                  "nb_status", "iucn_red_list_status", "sara_schedule", "cites_appendix", "responsible_authority", ]

    taxon = serializers.SerializerMethodField()
    cosewic_status = serializers.SerializerMethodField()
    sara_status = serializers.SerializerMethodField()
    ns_status = serializers.SerializerMethodField()
    nb_status = serializers.SerializerMethodField()
    iucn_red_list_status = serializers.SerializerMethodField()
    sara_schedule = serializers.SerializerMethodField()
    cites_appendix = serializers.SerializerMethodField()
    responsible_authority = serializers.SerializerMethodField()

    def get_taxon(self, instance):
        return instance.taxon.__str__()

    def get_cosewic_status(self, instance):
        return instance.cosewic_status.__str__()

    def get_sara_status(self, instance):
        return instance.sara_status.__str__()

    def get_ns_status(self, instance):
        return instance.ns_status.__str__()

    def get_nb_status(self, instance):
        return instance.nb_status.__str__()

    def get_iucn_red_list_status(self, instance):
        return instance.iucn_red_list_status.__str__()

    def get_sara_schedule(self, instance):
        return instance.sara_schedule.__str__()

    def get_cites_appendix(self, instance):
        return instance.cites_appendix.__str__()

    def get_responsible_authority(self, instance):
        return instance.responsible_authority.__str__()
