from rest_framework import serializers

from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import nz
from .. import models


class ComitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Committee
        fields = "__all__"

    main_topic = serializers.SerializerMethodField()
    species = serializers.SerializerMethodField()
    lead_region = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()
    division = serializers.SerializerMethodField()
    area_office = serializers.SerializerMethodField()
    area_office_program = serializers.SerializerMethodField()
    external_chair = serializers.SerializerMethodField()
    dfo_liaison = serializers.SerializerMethodField()
    other_dfo_branch = serializers.SerializerMethodField()
    other_dfo_regions = serializers.SerializerMethodField()
    lead_national_sector = serializers.SerializerMethodField()
    other_dfo_participants = serializers.SerializerMethodField()
    external_contact = serializers.SerializerMethodField()
    external_organization = serializers.SerializerMethodField()
    other_dfo_areas = serializers.SerializerMethodField()

    def get_main_topic(self, instance):
        return listrify([str(nz(t)) for t in instance.main_topic.all()])

    def get_species(self, instance):
        return listrify([str(nz(t)) for t in instance.species.all()])

    def get_external_chair(self, instance):
        return listrify([str(nz(t)) for t in instance.external_chair.all()])

    def get_dfo_liaison(self, instance):
        return listrify([str(nz(t)) for t in instance.dfo_liaison.all()])

    def get_other_dfo_branch(self, instance):
        return listrify([str(nz(t)) for t in instance.other_dfo_branch.all()])

    def get_other_dfo_regions(self, instance):
        return listrify([str(nz(t)) for t in instance.other_dfo_regions.all()])

    def get_other_dfo_areas(self, instance):
        return listrify([str(nz(t)) for t in instance.other_dfo_areas.all()])

    def get_dfo_national_sectors(self, instance):
        return listrify([str(nz(t)) for t in instance.dfo_national_sectors.all()])

    def get_other_dfo_participants(self, instance):
        return listrify([str(nz(t)) for t in instance.other_dfo_participants.all()])

    def get_external_contact(self, instance):
        return listrify([str(nz(t)) for t in instance.external_contact.all()])

    def get_external_organization(self, instance):
        return listrify([str(nz(t)) for t in instance.external_organization.all()])

    def get_lead_region(self, instance):
        return instance.lead_region.__str__()

    def get_branch(self, instance):
        return instance.branch.__str__()

    def get_division(self, instance):
        return instance.division.__str__()

    def get_area_office(self, instance):
        return instance.area_office.__str__()

    def get_area_office_program(self, instance):
        return instance.area_office_program.__str__()

    def get_lead_national_sector(self, instance):
        return instance.lead_national_sector.__str__()

