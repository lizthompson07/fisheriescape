from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext

from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, MetadataFields, Section, Organization, Lookup, FiscalYear

YES_NO_CHOICES = (
    (True, gettext("Yes")),
    (False, gettext("No")),
)


class Context(Lookup):
    word_limit = models.IntegerField(verbose_name=_("word limit"), default=500)


class Outcome(Lookup):
    context = models.ForeignKey(Context, on_delete=models.DO_NOTHING, verbose_name=_("context"), related_name="outcomes")
    name = models.CharField(max_length=255, verbose_name=_("name (en)"))
    # where as order is important, I am taking the easy way out and using model to order the formset (currently no other way to do this) - DJF
    description_en = models.TextField(blank=True, null=True, verbose_name=_("Description (en)"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("name (fr)"))
    description_fr = models.TextField(blank=True, null=True, verbose_name=_("Description (fr)"))

    class Meta:
        ordering = ["context", "name"]


class AchievementCategory(SimpleLookup):
    code = models.CharField(max_length=5, verbose_name=_("category code"))

    class Meta:
        ordering = ["code"]


class GroupLevel(UnilingualSimpleLookup):
    pass


class PublicationType(SimpleLookup):
    pass


class Application(MetadataFields):
    # Basic Information
    applicant = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("DM Apps user"), related_name="res_applications")
    current_group_level = models.ForeignKey(GroupLevel, on_delete=models.DO_NOTHING, related_name="applications_current",
                                            verbose_name=_("Current Group and Level"))
    current_position_title = models.CharField(max_length=100, verbose_name=_("Position Title"), blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name="applications", verbose_name=_("DFO Section"))
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, related_name="applications", verbose_name=_("Work Location"))
    last_application = models.DateTimeField(verbose_name=_("Last Application for Advancement"), blank=True, null=True)
    last_promotion = models.DateTimeField(verbose_name=_("Last Promotion"), blank=True, null=True)
    target_group_level = models.ForeignKey(GroupLevel, on_delete=models.DO_NOTHING, related_name="applications_target",
                                           verbose_name=_("Group and level being sought"))
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


class ApplicationOutcome(MetadataFields):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="outcomes")
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE, related_name="outcomes")
    text = models.TextField(blank=True, null=True, verbose_name=_("text"))


class ApplicationAchievement(MetadataFields):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="achievements")
    category = models.ForeignKey(AchievementCategory, on_delete=models.CASCADE, related_name="achievements")
    date = models.DateTimeField(verbose_name=_("date of publication / achievement"), editable=False)
    detail = models.TextField(verbose_name=_("detail"))
