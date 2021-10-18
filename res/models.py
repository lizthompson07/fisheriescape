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

    def __str__(self):
        return f"{self.context} - {self.tname}"


class AchievementCategory(SimpleLookup):
    code = models.CharField(max_length=5, verbose_name=_("category code"))
    is_publication = models.BooleanField(default=False, verbose_name=_("Is this a category for publications?"))

    class Meta:
        ordering = ["code"]


class GroupLevel(UnilingualSimpleLookup):
    pass


class PublicationType(SimpleLookup):
    pass


class Application(MetadataFields):
    # mandatories
    applicant = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_("researcher name"), related_name="res_applications")
    manager = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_("manager name"), related_name="manager_res_applications",
                                help_text=_("This is the person who will provide a recommendation on this application"))
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name="res_applications", verbose_name=_("DFO section"))
    current_group_level = models.ForeignKey(GroupLevel, on_delete=models.DO_NOTHING, related_name="applications_current",
                                            verbose_name=_("Current group / level"))
    target_group_level = models.ForeignKey(GroupLevel, on_delete=models.DO_NOTHING, related_name="applications_target",
                                           verbose_name=_("Group / level being sought"))
    application_start_date = models.DateTimeField(verbose_name=_("application start date"))
    application_end_date = models.DateTimeField(verbose_name=_("application end date"))

    current_position_title = models.CharField(max_length=255, verbose_name=_("position title"), blank=True, null=True)
    work_location = models.CharField(max_length=1000, verbose_name=_("work location"), blank=True, null=True)
    last_application = models.DateTimeField(verbose_name=_("last application for advancement"), blank=True, null=True)
    last_promotion = models.DateTimeField(verbose_name=_("last promotion"), blank=True, null=True)
    academic_background = models.TextField(blank=True, null=True, verbose_name=_("academic background"))
    employment_history = models.TextField(blank=True, null=True, verbose_name=_("employment history"))
    objectives = models.TextField(blank=True, null=True, verbose_name=_("department / sectoral objectives"), help_text=_("no more than 200 words"))
    relevant_factors = models.TextField(blank=True, null=True, verbose_name=_("relevant factors"), help_text=_("no more than 400 words"))

    # non-editables
    submission_date = models.DateTimeField(verbose_name=_("submission date"), blank=True, null=True, editable=False)

    # calculated
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("fiscal year"),
                                    related_name="res_applications", editable=False)
    status = models.IntegerField(default=10, verbose_name=_("status"), choices=model_choices.application_status_choices, editable=False)

    def save(self, *args, **kwargs):
        self.fiscal_year_id = fiscal_year(self.application_end_date, sap_style=True)

        # look at the review to help determine the status
        self.status = 10  # draft
        if self.submission_date:
            self.status = 20  # submitted
        elif self.submission_date and hasattr(self, "recommendation") and self.recommendation.id:
            self.status = 30  # submitted
            if self.recommendation.manager_signed:
                self.status = 40  #
            if self.recommendation.applicant_signed:
                self.status = 50  #
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

    @property
    def is_complete(self):
        """placeholder"""
        return True


class Recommendation(MetadataFields):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="recommendation")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("manager"), related_name="res_recommendations")
    recommendation_text = models.TextField(blank=True, null=True, verbose_name=_("manager's assessment"), help_text=_("no more than 250 words"))
    decision = models.IntegerField(verbose_name=_("decision"), choices=model_choices.decision_choices, blank=True, null=True)
    applicant_comment = models.TextField(blank=True, null=True, verbose_name=_("researcher's comment"), help_text=_("no more than 250 words"))

    # non-editables
    manager_signed = models.DateTimeField(verbose_name=_("signed by manager"), editable=False, blank=True, null=True)
    applicant_signed = models.DateTimeField(verbose_name=_("signed by researcher"), editable=False, blank=True, null=True)

    @property
    def recommendation_text_html(self):
        if self.recommendation_text:
            return markdown(self.recommendation_text)

    @property
    def applicant_comment_html(self):
        if self.applicant_comment:
            return markdown(self.applicant_comment)


class ApplicationOutcome(MetadataFields):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="outcomes")
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE, related_name="outcomes")
    text = models.TextField(blank=True, null=True, verbose_name=_("text"))

    def __str__(self):
        return f"{self.outcome}"

    @property
    def text_html(self):
        if self.text:
            return markdown(self.text)


class Achievement(MetadataFields):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="achievements")
    category = models.ForeignKey(AchievementCategory, on_delete=models.CASCADE, related_name="achievements", blank=True, null=True,
                                 verbose_name=_("achievement category"))
    publication_type = models.ForeignKey(PublicationType, on_delete=models.CASCADE, related_name="achievements", blank=True, null=True,
                                         verbose_name=_("publication type"))
    date = models.DateTimeField(verbose_name=_("date of publication / achievement"), blank=True, null=True)
    detail = models.CharField(verbose_name=_("detail"), blank=True, null=True, max_length=2000)

    class Meta:
        ordering = ["application", "category", "publication_type", "-date"]

    def __str__(self):
        return f"{self.category}"

    @property
    def achievement_display(self):
        cat = "<span class='red-font'>{text}</span>".format(text=gettext("missing category"))
        pub_type = "<span class='red-font'>{text}</span>".format(text=gettext("missing publication type"))
        fy = "<span class='red-font'>{text}</span>".format(text=gettext("missing fiscal year"))
        detail = "<span class='red-font'>{text}</span>".format(text=gettext("missing detail"))
        dt = "<span class='red-font'>{text}</span>".format(text=gettext("missing date"))

        if self.publication_type:
            pub_type = self.publication_type

        if self.category:
            if self.is_publication:
                cat = f"{self.category} - {pub_type}"
            else:
                cat = str(self.category)

        if self.date:
            fy = fiscal_year(self.date)
            dt = self.date.strftime("%Y-%m-%d")

        if self.detail:
            detail = self.detail

        mystr = f"{cat} ({fy}) {detail} - {dt}"
        return mystr

    @property
    def is_publication(self):
        return self.category and self.category.is_publication
