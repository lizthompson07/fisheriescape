from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.db import models

from django.utils.translation import gettext_lazy as _

from shared_models import models as shared_models
from masterlist import models as ml_models


YES_NO_CHOICES = [(True, _("Yes")), (False, _("No")), ]

NULL_YES_NO_CHOICES = (
    (None, _("---------")),
    (1, _("Yes")),
    (0, _("No")),
)

ROLE_DFO_CHOICES = (
    (None, _("---------")),
    (1, "Programs"),
    (2, "Manager"),
    (3, "Director"),
    (13, "Area Director"),
    (4, "Regional Director"),
    (5, "Associate Regional Director General"),
    (6, "Regional Director General"),
    (7, "Director General"),
    (8, "Assistant Deputy Minister"),
    (9, "Senior Assistant Deputy Minister"),
    (10, "Deputy Minister"),
    (11, "Minister"),
    (12, "Unknown"),
)

Q_HIDE_BRANCHES = (~Q(name__contains="SORTING") &
                   ~Q(name__icontains="Fisheries Management, Resource and Aboriginal Fisheries Management"))


class MaretUser(models.Model):
    mode_choices = (
        (1, "read"),
        (2, "edit"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="maret_user", verbose_name=_("DM Apps user"))
    # admins can modify helptext and other app settings
    is_admin = models.BooleanField(default=False, verbose_name=_("app administrator"), choices=YES_NO_CHOICES)
    # authors can create/modify/delete records
    is_author = models.BooleanField(default=False, verbose_name=_("app author"), choices=YES_NO_CHOICES)
    # users can view, but not modify records
    is_user = models.BooleanField(default=False, verbose_name=_("app user"), choices=YES_NO_CHOICES)

    # admin users can toggle helptext edit mode on and off
    mode = models.IntegerField(choices=mode_choices, default=1)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_admin", "user__first_name", ]


class DiscussionTopic(shared_models.SimpleLookup):
    pass


class Species(shared_models.SimpleLookup):
    pass


class Area(shared_models.SimpleLookup):
    pass


class OrgCategory(shared_models.SimpleLookup):
    pass


class AreaOffice(shared_models.SimpleLookup):
    pass


class AreaOfficeProgram(shared_models.SimpleLookup):
    # need to make name not unique as multiple area_offices can have the same name
    name = models.CharField(unique=False, max_length=255, verbose_name=_("name (en)"))

    area_office = models.ForeignKey(AreaOffice, blank=True, null=True, default=None, on_delete=models.DO_NOTHING,
                                    verbose_name=_("Area Office Program"))

    class Meta:
        unique_together = ['name', 'area_office']


class Committee(models.Model):
    meeting_frequency_choices = (
        (0, "Monthly"),
        (1, "Once a year"),
        # (2, 1-2 times a year), # removed 12, april, 2022
        (3, "Twice a year"),
        # (4, 2-3 times a year), # removed 12, april, 2022
        (5, "Three times a year"),
        (6, "Four times a year"),
        (7, "As needed"),
        (8, "Every other year"),
        (9, "Other"),
    )

    name = models.CharField(max_length=255, verbose_name=_("Name of committee/Working Group"))
    main_topic = models.ManyToManyField(DiscussionTopic, blank=True, related_name="committee_main_topics",
                                        verbose_name=_("Main Topic(s) of discussion"))
    species = models.ManyToManyField(Species, blank=True, related_name="committee_species",
                                     verbose_name=_("Main species of discussion"))
    lead_region = models.ForeignKey(shared_models.Region, related_name="committee_lead_dfo_region",
                                    blank=True, null=True, verbose_name=_("Lead DFO region"),
                                    on_delete=models.DO_NOTHING,
                                    )
    branch = models.ForeignKey(shared_models.Branch, blank=True, null=True, default=1, on_delete=models.DO_NOTHING,
                               related_name="committee_branch", verbose_name=_("Lead DFO Maritimes Region branch"),
                               limit_choices_to=Q(region__name="Maritimes") & Q_HIDE_BRANCHES)
    division = models.ForeignKey(shared_models.Division, blank=True, null=True, on_delete=models.DO_NOTHING,
                                 verbose_name=_("Division within the specified lead branch"))
    area_office = models.ForeignKey(AreaOffice, blank=True, null=True, related_name="committee_area_office",
                                    on_delete=models.DO_NOTHING, verbose_name=_("Lead Maritimes Region area office"))
    area_office_program = models.ForeignKey(AreaOfficeProgram, blank=True, null=True,
                                            related_name="committee_area_office_program", on_delete=models.DO_NOTHING,
                                            verbose_name=_("Program within the specified lead area office"))

    # leaving this out for now because it may be a redundant filed included in the interactions model
    # role_dfo = models.IntegerField(choices=ROLE_DFO_CHOICES)
    is_dfo_chair = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES,
                                       verbose_name=_("Does DFO chair/co-chair"))

    external_chair = models.ManyToManyField(ml_models.Person, blank=True, verbose_name=_("External Chair"))
    dfo_liaison = models.ManyToManyField(User, blank=True, related_name="committee_dfo_liaison",
                                         verbose_name=_("DFO Maritimes Region liaison"))
    other_dfo_branch = models.ManyToManyField(shared_models.Branch, related_name="committee_dfo_branch",
                                              blank=True,  limit_choices_to=Q(region__name="Maritimes") & Q_HIDE_BRANCHES,
                                              verbose_name=_("Other participating DFO Maritimes Region branches")
                                              )
    other_dfo_regions = models.ManyToManyField(shared_models.Region, related_name="committee_dfo_region",
                                               blank=True, verbose_name=_("Other participating DFO regions"),
                                               limit_choices_to=~models.Q(name__in=["Maritimes"]),
                                               )
    other_dfo_areas = models.ManyToManyField(AreaOffice, related_name="committee_dfo_area",
                                             blank=True,  verbose_name=_("Other participating DFO Maritimes Region area offices")
                                             )
    dfo_national_sectors = models.ManyToManyField(shared_models.Sector, related_name="committee_sector",
                                                  blank=True,
                                                  verbose_name=_("Participating National Headquarters sectors"),
                                                  limit_choices_to={"region__name": "National"}
                                                  )
    lead_national_sector = models.ForeignKey(shared_models.Sector, related_name="committee_lead_sector",
                                             blank=True, null=True, verbose_name=_("Lead National sector"),
                                             limit_choices_to={"region__name": "National"}, on_delete=models.DO_NOTHING,
                                             )
    dfo_role = models.IntegerField(choices=ROLE_DFO_CHOICES, default=12,
                                   verbose_name="Highest level DFO participant")
    first_nation_participation = models.BooleanField(default=False,
                                                     verbose_name=_("Indigenous community/organization participation?"))
    municipal_participation = models.BooleanField(default=False,
                                                  verbose_name=_("Local/municipal government participation?"))
    provincial_participation = models.BooleanField(default=False,
                                                   verbose_name=_("Provincial government participation?"))
    other_federal_participation = models.BooleanField(default=False,
                                                      verbose_name=_("Other federal department/agency participation?"))
    other_dfo_participants = models.ManyToManyField(User, blank=True, related_name="committee_dfo_participants",
                                                    verbose_name=_(
                                                        "Other DFO Maritimes region participants/contributors"))
    external_contact = models.ManyToManyField(ml_models.Person, verbose_name=_("Other external contact(s)"),
                                              blank=True, related_name="committee_ext_contact")
    external_organization = models.ManyToManyField(ml_models.Organization, verbose_name=_("External Organization(s)"),
                                                   blank=True, related_name="committee_ext_organization")
    meeting_frequency = models.IntegerField(choices=meeting_frequency_choices, verbose_name=_("Meeting frequency"),
                                            default=1)
    are_tor = models.BooleanField(default=False, verbose_name=_("Are there terms of reference?"))
    location_of_tor = models.TextField(blank=True, null=True, verbose_name=_("Location of terms of reference"))
    main_actions = models.TextField(default="-----", verbose_name=_("Role of committee / working group"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("Comments"))
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True,
                                         verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
                                         verbose_name=_("last modified by"))

    def __str__(self):
        return self.name


class Interaction(models.Model):
    interaction_type_choices = (
        # (1, "Minister meeting"), # Removed 2022-08-02
        # (2, "Deputy Minister meeting"), # Removed 2022-08-02
        # (3, "Maritimes Region ad hoc meeting"), # Removed 2022-08-02
        # (4, "Committee / Working Group meeting"), # Removed 2022-08-02
        # (5, "Committee / Working Group correspondence"), # Removed 2021-11-16
        # (6, "Ministerial correspondence"), # Removed 2022-08-02
        # (7, "Deputy Minister correspondence"), # Removed 2022-08-02
        # (8, "Maritimes Region correspondence "), # Removed 2022-08-02
        # (9, "Conference or workshop "), # Removed 2022-08-02
        (10, "Email or other written correspondence "),
        (11, "In-person meeting"),
        (12, "Hybrid meeting"),
        (13, "Virtual or phone meeting "),
        (14, "Conference or workshop "),

    )

    description = models.CharField(max_length=255, default="N/A", verbose_name="Title of Interaction")
    interaction_type = models.IntegerField(choices=interaction_type_choices, blank=True, null=True, default=None)
    is_committee = models.BooleanField(default=False, verbose_name=_("Committee or Working Group"), choices=YES_NO_CHOICES)
    committee = models.ForeignKey(Committee, blank=True, null=True, on_delete=models.DO_NOTHING,
                                  verbose_name="Committee / Working Group", related_name="committee_interactions")
    dfo_role = models.IntegerField(choices=ROLE_DFO_CHOICES, default=None,
                                   verbose_name="Highest level DFO participant")
    dfo_liaison = models.ManyToManyField(User, blank=True, related_name="interaction_dfo_liaison",
                                         verbose_name=_("DFO Maritimes Region liaison"))
    other_dfo_participants = models.ManyToManyField(User, blank=True, related_name="interaction_dfo_participants",
                                                    verbose_name=_("Other DFO Maritimes region participants/contributors"))
    branch = models.ForeignKey(shared_models.Branch, blank=True, null=True, default=None, on_delete=models.DO_NOTHING,
                               related_name="interaction_branch", verbose_name=_("Lead DFO Maritimes branch"),
                               limit_choices_to=Q(region__name="Maritimes") & Q_HIDE_BRANCHES)
    area_office = models.ForeignKey(AreaOffice, blank=True, null=True, related_name="interaction_area_office",
                                    on_delete=models.DO_NOTHING, verbose_name=_("Lead DFO Maritimes Region area office"))
    area_office_program = models.ForeignKey(AreaOfficeProgram, blank=True, null=True,
                                            related_name="interaction_area_office_program", on_delete=models.DO_NOTHING,
                                            verbose_name=_("Program within the specified lead area office"))
    division = models.ForeignKey(shared_models.Division, blank=True, null=True, on_delete=models.DO_NOTHING,
                                 verbose_name=_("Division within the specified lead branch"))
    other_dfo_branch = models.ManyToManyField(shared_models.Branch, related_name="interaction_dfo_branch",
                                              blank=True, limit_choices_to=Q(region__name="Maritimes") & Q_HIDE_BRANCHES,
                                              verbose_name=_("Other participating DFO Maritimes Region branches")
                                              )
    lead_region = models.ForeignKey(shared_models.Region, related_name="interaction_lead_dfo_region",
                                    blank=True, null=True, verbose_name=_("Lead DFO region"),
                                    on_delete=models.DO_NOTHING,
                                    )
    other_dfo_regions = models.ManyToManyField(shared_models.Region, related_name="interaction_dfo_region",
                                               blank=True, verbose_name=_("Other participating DFO regions"),
                                               limit_choices_to=~models.Q(name__in=["Maritimes"]),
                                               )
    dfo_national_sectors = models.ManyToManyField(shared_models.Sector, related_name="interaction_sector",
                                                  blank=True, verbose_name=_("Participating National Headquarters sectors"),
                                                  limit_choices_to={"region__name": "National"}
                                                  )
    lead_national_sector = models.ForeignKey(shared_models.Sector, related_name="interaction_lead_sector",
                                             blank=True, null=True, verbose_name=_("Lead National sector"),
                                             limit_choices_to={"region__name": "National"}, on_delete=models.DO_NOTHING
                                             )
    other_dfo_areas = models.ManyToManyField(AreaOffice, related_name="interaction_dfo_area",
                                             blank=True, verbose_name=_("Other participating DFO Maritimes Region area offices")
                                             )
    external_contact = models.ManyToManyField(ml_models.Person, verbose_name=_("External contact(s)"),
                                              blank=True, related_name="interaction_ext_contact")
    external_organization = models.ManyToManyField(ml_models.Organization, verbose_name=_("External Organization(s)"),
                                                   blank=True, related_name="interaction_ext_organization")
    date_of_meeting = models.DateTimeField(blank=True, null=True, default=timezone.now,
                                           verbose_name=_("Date of Interaction"))
    main_topic = models.ManyToManyField(DiscussionTopic, blank=True, related_name="main_topics",
                                        verbose_name=_("Main Topic(s) of discussion"))
    species = models.ManyToManyField(Species, blank=True, related_name="species",
                                     verbose_name=_("Main species of discussion"))
    action_items = models.TextField(default="-----", verbose_name=_("Main results"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("Comments"))
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True,
                                         verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
                                         verbose_name=_("last modified by"))

    def __str__(self):
        return "{}: {}".format(self.pk, self.description)


class OrganizationExtension(models.Model):
    organization = models.ForeignKey(ml_models.Organization, blank=False, null=False, default=1, related_name="ext_org",
                                     verbose_name="Organization", on_delete=models.CASCADE)
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail", )
    associated_provinces = models.ManyToManyField(shared_models.Province, related_name="ext_asc_province",
                                                  verbose_name="Associated Provinces")
    category = models.ManyToManyField(OrgCategory, related_name="ext_org_category", verbose_name="Category")
    area = models.ManyToManyField(Area, related_name="ext_org_area", verbose_name="Area")


class ContactExtension(models.Model):
    committee = models.ManyToManyField(Committee, blank=True, related_name="contact_committees",
                                       verbose_name=_("Committee / Working Group Membership"))
    contact = models.ForeignKey(ml_models.Person, blank=False, null=False, default=1, related_name="ext_con",
                                verbose_name="Contact", on_delete=models.CASCADE)


# This is a special table used to house application help text
class HelpText(models.Model):
    model = models.CharField(max_length=255, blank=True, null=True)
    field_name = models.CharField(max_length=255)
    eng_text = models.TextField(verbose_name=_("English text"))
    fra_text = models.TextField(blank=True, null=True, verbose_name=_("French text"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("eng_text"))):
            return "{}".format(getattr(self, str(_("eng_text"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.eng_text)

    class Meta:
        ordering = ['field_name', ]
