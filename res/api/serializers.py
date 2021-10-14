from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.template.defaultfilters import date
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
    academic_background_html = serializers.SerializerMethodField()
    employment_history_html = serializers.SerializerMethodField()
    objectives_html = serializers.SerializerMethodField()
    relevant_factors_html = serializers.SerializerMethodField()
    applicant_display = serializers.SerializerMethodField()

    target_group_level_display = serializers.SerializerMethodField()
    current_group_level_display = serializers.SerializerMethodField()
    section_display = serializers.SerializerMethodField()

    application_end_date_display = serializers.SerializerMethodField()
    application_start_date_display = serializers.SerializerMethodField()

    last_application_display = serializers.SerializerMethodField()
    last_promotion_display = serializers.SerializerMethodField()
    application_range_description = serializers.SerializerMethodField()

    def get_application_range_description(self, instance):
        return instance.application_range_description

    def get_last_application_display(self, instance):
        return naturaltime(instance.last_application)

    def get_last_promotion_display(self, instance):
        return naturaltime(instance.last_promotion)

    def get_application_start_date_display(self, instance):
        return date(instance.application_start_date)

    def get_application_end_date_display(self, instance):
        return date(instance.application_end_date)

    def get_section_display(self, instance):
        return instance.section.full_name

    def get_target_group_level_display(self, instance):
        return str(instance.target_group_level)

    def get_current_group_level_display(self, instance):
        return str(instance.current_group_level)

    def get_applicant_display(self, instance):
        return str(instance.applicant)

    def get_academic_background_html(self, instance):
        return instance.academic_background_html

    def get_employment_history_html(self, instance):
        return instance.employment_history_html

    def get_objectives_html(self, instance):
        return instance.objectives_html

    def get_relevant_factors_html(self, instance):
        return instance.relevant_factors_html

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

    def validate(self, attrs):
        """
        form validation:
        - make sure that last promotion is in the past
        - make sure that last application is in the past
        - make sure that application end date is after application start date
        """
        application_start_date = attrs.get("application_start_date")
        application_end_date = attrs.get("application_end_date")
        last_promotion = attrs.get("last_promotion")
        last_application = attrs.get("last_application")

        if application_end_date < application_start_date:
            msg = _('The application end date must be after the application start date')
            raise ValidationError(msg)

        if last_application > timezone.now():
            msg = _('The date of your last application must be in the past')
            raise ValidationError(msg)

        if last_promotion > timezone.now():
            msg = _('The date of your last promotion must be in the past')
            raise ValidationError(msg)

        return attrs
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
