from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext

from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, MetadataFields, Section, Organization

YES_NO_CHOICES = (
    (True, gettext("Yes")),
    (False, gettext("No")),
)


class GroupLevel(UnilingualSimpleLookup):
    pass


class Context(SimpleLookup):
    word_limit = models.IntegerField(verbose_name=_("word limit"), default=500)


class Application(MetadataFields):
    # Basic Information
    applicant = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("DM Apps user"), related_name="res_applications")
    current_group_level = models.ForeignKey(GroupLevel, on_delete=models.DO_NOTHING, related_name="applications_current", verbose_name=_("Current Group and Level"))
    current_position_title = models.CharField(max_length=100, verbose_name=_("Position Title"), blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name="applications", verbose_name=_("DFO Section"))
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, related_name="applications", verbose_name=_("Work Location"))
    last_application = models.DateTimeField(verbose_name=_("Last Application for Advancement"), blank=True, null=True)
    last_promotion = models.DateTimeField(verbose_name=_("Last Promotion"), blank=True, null=True)
    target_group_level = models.ForeignKey(GroupLevel, on_delete=models.DO_NOTHING, related_name="applications_target", verbose_name=_("Group and level being sought"))
    application_start_date = models.DateTimeField(verbose_name=_("application start date"))
    application_end_date = models.DateTimeField(verbose_name=_("application end date"))
    academic_background = models.TextField(blank=True, null=True, verbose_name=_("Academic Background"))
    employment_history = models.TextField(blank=True, null=True, verbose_name=_("Employment History"))
    objectives = models.TextField(blank=True, null=True, verbose_name=_("Department / Sectoral Objectives"), help_text=_("no more than 200 words"))
    relevant_factors = models.TextField(blank=True, null=True, verbose_name=_("Relevant Factors"), help_text=_("no more than 400 words"))


class Recommendation(MetadataFields):
    decision_choices = (
        (0, _("In my opinion, the dossier contains sufficient evidence to warrant consideration of the application by the appropriate committee.")),
        (1, _("In my opinion, the dossier does not contain sufficient evidence to warrant consideration of the application by the appropriate committee.")),
    )
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="recommendations")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("DM Apps user"), related_name="res_recommendations")
    recommendation_text = models.TextField(blank=True, null=True, verbose_name=_("recommendation text"), help_text=_("no more than 250 words"))
    decision = models.IntegerField(verbose_name=_("Recommendation decision"), choices=decision_choices)
    manager_signed = models.DateTimeField(verbose_name=_("date signed by manager"), editable=False)
    applicant_comment = models.TextField(blank=True, null=True, verbose_name=_("applicant comments (optional)"), help_text=_("no more than 250 words"))
    applicant_signed = models.DateTimeField(verbose_name=_("date signed by applicant"), editable=False)


class Outcome(MetadataFields):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="outcomes")
    context = models.ForeignKey(Context, on_delete=models.DO_NOTHING, verbose_name=_("context"), related_name="outcomes")
    # recommendation_text = models.TextField(blank=True, null=True, verbose_name=_("recommendation text"), help_text=_("no more than 250 words"))
    # decision = models.IntegerField(verbose_name=_("Recommendation decision"), choices=decision_choices)
    # manager_signed = models.DateTimeField(verbose_name=_("date signed by manager"), editable=False)
    # applicant_comment = models.TextField(blank=True, null=True, verbose_name=_("applicant comments (optional)"), help_text=_("no more than 250 words"))
    # applicant_signed = models.DateTimeField(verbose_name=_("date signed by applicant"), editable=False)


