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
    recommendation = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField()
    manager_display = serializers.SerializerMethodField()
    submission_date = serializers.SerializerMethodField()
    context_word_count_dict = serializers.SerializerMethodField()
    achievement_categories = serializers.SerializerMethodField()
    achievement_publication_types = serializers.SerializerMethodField()

    def get_achievement_publication_types(self, instance):
        return PublicationTypeSerializer(instance.achievement_publication_types, many=True, read_only=True).data

    def get_achievement_categories(self, instance):
        return AchievementCategorySerializer(instance.achievement_categories, many=True, read_only=True).data

    def get_context_word_count_dict(self, instance):
        return instance.context_word_count_dict

    def get_submission_date(self, instance):
        return date(instance.submission_date)

    def get_manager_display(self, instance):
        return str(instance.manager)

    def get_is_complete(self, instance):
        return instance.is_complete

    def get_recommendation(self, instance):
        if hasattr(instance, "recommendation"):
            return instance.recommendation.id

    def get_application_range_description(self, instance):
        return instance.application_range_description

    def get_last_application_display(self, instance):
        return f"{date(instance.last_application)} ({naturaltime(instance.last_application)})"

    def get_last_promotion_display(self, instance):
        return f"{date(instance.last_promotion)} ({naturaltime(instance.last_promotion)})"

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

        if last_application and last_application > timezone.now():
            msg = _('The date of your last application must be in the past')
            raise ValidationError(msg)

        if last_promotion and last_promotion > timezone.now():
            msg = _('The date of your last promotion must be in the past')
            raise ValidationError(msg)

        return attrs


class RecommendationSerializer(serializers.ModelSerializer):
    recommendation_text_html = serializers.SerializerMethodField()
    applicant_comment_html = serializers.SerializerMethodField()
    manager_signed_display = serializers.SerializerMethodField()
    applicant_signed_display = serializers.SerializerMethodField()
    decision_display = serializers.SerializerMethodField()

    def get_decision_display(self, instance):
        return instance.get_decision_display()

    def get_manager_signed_display(self, instance):
        return instance.manager_signature

    def get_applicant_signed_display(self, instance):
        return instance.applicant_signature

    def get_applicant_comment_html(self, instance):
        return instance.applicant_comment_html

    def get_recommendation_text_html(self, instance):
        return instance.recommendation_text_html

    class Meta:
        model = models.Recommendation
        fields = "__all__"


class ApplicationOutcomeSerializer(serializers.ModelSerializer):
    text_html = serializers.SerializerMethodField()
    created_at_display = serializers.SerializerMethodField()
    updated_at_display = serializers.SerializerMethodField()
    outcome_display = serializers.SerializerMethodField()
    word_count = serializers.SerializerMethodField()

    def get_word_count(self, instance):
        return instance.word_count

    def get_outcome_display(self, instance):
        return str(instance.outcome)

    def get_created_at_display(self, instance):
        return date(instance.created_at, "DATETIME_FORMAT")

    def get_updated_at_display(self, instance):
        return date(instance.updated_at, "DATETIME_FORMAT")

    def get_text_html(self, instance):
        return instance.text_html

    class Meta:
        model = models.ApplicationOutcome
        fields = "__all__"


class AchievementSerializer(serializers.ModelSerializer):
    created_at_display = serializers.SerializerMethodField()
    updated_at_display = serializers.SerializerMethodField()
    date_display = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    publication_type_display = serializers.SerializerMethodField()
    achievement_display = serializers.SerializerMethodField()
    is_publication = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    achievement_display_no_code = serializers.SerializerMethodField()

    def get_achievement_display_no_code(self, instance):
        return instance.achievement_display_no_code

    def get_code(self, instance):
        return instance.code

    def get_is_publication(self, instance):
        return instance.is_publication

    def get_achievement_display(self, instance):
        return instance.achievement_display

    def get_category_display(self, instance):
        if instance.category:
            return str(instance.category)

    def get_publication_type_display(self, instance):
        if instance.publication_type:
            return str(instance.publication_type)

    def get_date_display(self, instance):
        if instance.date:
            return date(instance.date)

    def get_created_at_display(self, instance):
        return date(instance.created_at, "DATETIME_FORMAT")

    def get_updated_at_display(self, instance):
        return date(instance.updated_at, "DATETIME_FORMAT")

    class Meta:
        model = models.Achievement
        fields = "__all__"


class OutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Outcome
        fields = "__all__"

    tname = serializers.SerializerMethodField()
    tdescription = serializers.SerializerMethodField()
    description_html = serializers.SerializerMethodField()

    def get_description_html(self, instance):
        return instance.description_html
    
    def get_tdescription(self, instance):
        return instance.tdescription

    def get_tname(self, instance):
        return instance.tname


class ContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Context
        fields = "__all__"

    outcomes = OutcomeSerializer(read_only=False, many=True)
    tname = serializers.SerializerMethodField()
    tdescription = serializers.SerializerMethodField()

    def get_tdescription(self, instance):
        return instance.tdescription

    def get_tname(self, instance):
        return instance.tname


class PublicationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PublicationType
        fields = "__all__"

    tname = serializers.SerializerMethodField()

    def get_tname(self, instance):
        return instance.tname


class AchievementCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AchievementCategory
        fields = "__all__"

    tname = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()

    def get_display(self, instance):
        return instance.display1

    def get_tname(self, instance):
        return instance.tname

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
