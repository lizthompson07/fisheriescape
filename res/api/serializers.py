from django.contrib.auth.models import User
from rest_framework import serializers

from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class ApplicationSerializer(serializers.ModelSerializer):
    status_display_html = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    fiscal_year_display = serializers.SerializerMethodField()
    status_display_html = serializers.SerializerMethodField()
    academic_background_html = serializers.SerializerMethodField()
    employment_history_html = serializers.SerializerMethodField()
    objectives_html = serializers.SerializerMethodField()

    def get_status_display_html(self, instance):
        return instance.status_display_html

    def get_academic_background_html(self, instance):
        return instance.academic_background_html

    def get_employment_history_html(self, instance):
        return instance.employment_history_html

    def get_objectives_html(self, instance):
        return instance.objectives_html

    def get_fiscal_year_display(self, instance):
        return str(instance.fiscal_year)

    def get_metadata(self, instance):
        return instance.metadata

    def get_status_display_html(self, instance):
        return instance.status_display_html

    def get_status_display(self, instance):
        return instance.get_status_display()

    class Meta:
        model = models.Application
        fields = "__all__"
#
#
# class ObservationSerializer(serializers.ModelSerializer):
#     section = SectionLITESerializer(read_only=True)
#     sex_display = serializers.SerializerMethodField()
#     egg_status_display = serializers.SerializerMethodField()
#     certainty_rating_display = serializers.SerializerMethodField()
#
#     def get_certainty_rating_display(self, instance):
#         return instance.certainty_rating_special_display
#
#     def get_egg_status_display(self, instance):
#         return instance.egg_status_special_display
#
#     def get_sex_display(self, instance):
#         return instance.sex_special_display
#
#     class Meta:
#         model = models.Observation
#         fields = "__all__"
#
#
# class SectionSerializer(serializers.ModelSerializer):
#     observations = ObservationSerializer(many=True, read_only=True)
#     substrate_profile = serializers.SerializerMethodField()
#
#     def get_substrate_profile(self, instance):
#         return instance.substrate_profile
#
#     class Meta:
#         model = models.Section
#         fields = "__all__"
