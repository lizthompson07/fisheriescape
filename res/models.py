from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _, gettext, get_language, activate
from markdown import markdown

from lib.functions.custom_functions import fiscal_year
from lib.templatetags.custom_filters import timedelta_duration_days
from res import model_choices
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
    # mandatories
    applicant = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_("applicant name"), related_name="res_applications")
    current_group_level = models.ForeignKey(GroupLevel, on_delete=models.DO_NOTHING, related_name="applications_current", verbose_name=_("Current Group/Level"))
    target_group_level = models.ForeignKey(GroupLevel, on_delete=models.DO_NOTHING, related_name="applications_target",
                                           verbose_name=_("Group/level being sought"))
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name="res_applications", verbose_name=_("DFO Section"))
    application_start_date = models.DateTimeField(verbose_name=_("application start date"))
    application_end_date = models.DateTimeField(verbose_name=_("application end date"))

    current_position_title = models.CharField(max_length=255, verbose_name=_("Position Title"), blank=True, null=True)
    work_location = models.CharField(max_length=1000, verbose_name=_("Work Location"), blank=True, null=True)
    last_application = models.DateTimeField(verbose_name=_("Last Application for Advancement"), blank=True, null=True)
    last_promotion = models.DateTimeField(verbose_name=_("Last Promotion"), blank=True, null=True)
    academic_background = models.TextField(blank=True, null=True, verbose_name=_("Academic Background"))
    employment_history = models.TextField(blank=True, null=True, verbose_name=_("Employment History"))
    objectives = models.TextField(blank=True, null=True, verbose_name=_("Department / Sectoral Objectives"), help_text=_("no more than 200 words"))
    relevant_factors = models.TextField(blank=True, null=True, verbose_name=_("Relevant Factors"), help_text=_("no more than 400 words"))

    # non-editables
    submission_date = models.DateTimeField(verbose_name=_("submission date"), blank=True, null=True, editable=False)

    # calculated
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("fiscal year"),
                                    related_name="res_applications", editable=False)
    status = models.IntegerField(default=10, verbose_name=_("status"), choices=model_choices.application_status_choices, editable=False)

    def save(self, *args, **kwargs):
        self.fiscal_year_id = fiscal_year(self.application_end_date, sap_style=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.applicant} ({self.target_group_level})"

    @property
    def application_range_description(self):
        return timedelta_duration_days(self.application_end_date - self.application_start_date)

    @property
    def region(self):
        return self.section.division.branch.sector.region

    def get_absolute_url(self):
        return reverse('res:application_detail', kwargs={'pk': self.id})

    @property
    def status_class(self):
        lang = get_language()
        activate("en")
        mystr = slugify(self.get_status_display()) if self.status else ""
        activate(lang)
        return mystr

    @property
    def status_display_html(self):
        return f'<span class=" px-1 py-1 {self.status_class}">{self.get_status_display()}</span>'

    @property
    def academic_background_html(self):
        if self.academic_background:
            return markdown(self.academic_background)

    @property
    def employment_history_html(self):
        if self.employment_history:
            return markdown(self.employment_history)

    @property
    def objectives_html(self):
        if self.objectives:
            return markdown(self.objectives)

    @property
    def relevant_factors_html(self):
        if self.relevant_factors:
            return markdown(self.relevant_factors)


class Recommendation(MetadataFields):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="recommendation")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("DM Apps user"), related_name="res_recommendations")
    recommendation_text = models.TextField(blank=True, null=True, verbose_name=_("recommendation text"), help_text=_("no more than 250 words"))
    decision = models.IntegerField(verbose_name=_("Recommendation decision"), choices=model_choices.decision_choices)
    applicant_comment = models.TextField(blank=True, null=True, verbose_name=_("applicant comments (optional)"), help_text=_("no more than 250 words"))

    # non-editables
    manager_signed = models.DateTimeField(verbose_name=_("date signed by manager"), editable=False)
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
