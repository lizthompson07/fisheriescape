from django.contrib.auth.models import User
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


class MaretAdminUser(models.Model):
    mode_choices = (
        (1, "read"),
        (2, "edit"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="maret_admin_user", verbose_name=_("DM Apps user"))
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


class Committee(models.Model):
    meeting_frequency_choices = (
        (0, "Monthly"),
        (1, "Once a year"),
        (2, "1-2 times per year"),
        (3, "Twice a year"),
        (4, "2-3 times per year"),
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
    branch = models.ForeignKey(shared_models.Branch, default=1, on_delete=models.DO_NOTHING,
                               related_name="committee_branch", verbose_name=_("Lead DFO branch"))
    area_office = models.ManyToManyField(AreaOffice, blank=True, related_name="committee_area_office",
                                         verbose_name=_("Area Office"))
    division = models.ForeignKey(shared_models.Division, default=1, blank=True, null=True, on_delete=models.DO_NOTHING,
                                 verbose_name=_("Division"))

    # leaving this out for now because it may be a redundant filed included in the interactions model
    # role_dfo = models.IntegerField(choices=ROLE_DFO_CHOICES)
    is_dfo_chair = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES,
                                       verbose_name=_("Does DFO chair/co-chair"))

    external_chair = models.ForeignKey(ml_models.Person, blank=True, null=True, on_delete=models.DO_NOTHING,
                                       verbose_name=_("External Chair"))
    dfo_liaison = models.ManyToManyField(User, related_name="committee_dfo_liaison",
                                         verbose_name=_("DFO liaison/secretariat"))
    other_dfo_branch = models.ManyToManyField(shared_models.Branch, related_name="committee_dfo_branch",
                                              verbose_name=_("Other participating DFO branches/regions/area offices")
                                              )
    dfo_role = models.IntegerField(choices=ROLE_DFO_CHOICES, default=12,
                                   verbose_name="Role of highest level DFO participant")
    first_nation_participation = models.BooleanField(default=False,
                                                     verbose_name=_("First Nations/Indigenous group participation?"))
    provincial_participation = models.BooleanField(default=False,
                                                   verbose_name=_("Provincial government participation?"))
    external_contact = models.ManyToManyField(ml_models.Person, verbose_name=_("External Contact(s)"),
                                              blank=True,related_name="committee_ext_contact")
    external_organization = models.ManyToManyField(ml_models.Organization, verbose_name=_("External Organization(s)"),
                                                   blank=True, related_name="committee_ext_organization")
    meeting_frequency = models.IntegerField(choices=meeting_frequency_choices, verbose_name=_("Meeting frequency"),
                                            default=1)
    are_tor = models.BooleanField(default=False, verbose_name=_("Are there terms of reference?"))
    location_of_tor = models.TextField(blank=True, null=True, verbose_name=_("Location of terms of reference"))
    main_actions = models.TextField(default="-----", verbose_name=_("Main actions"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("Comments"))
    last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now,
                                         verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
                                         verbose_name=_("last modified by"))

    def __str__(self):
        return self.name


class Interaction(models.Model):
    interaction_type_choices = (
        (1, "Minister meeting"),
        (2, "Deputy Minister meeting"),
        (3, "Maritimes Region ad hoc meeting"),
        (4, "Committee / Working Group meeting"),
        # (5, "Committee / Working Group correspondence"), # Removed 2021-11-16
        (6, "Ministerial correspondence"),
        (7, "Deputy Minister correspondence"),
        (8, "Maritimes Region correspondence "),
    )

    description = models.CharField(max_length=255, default="N/A", verbose_name="Short Description")
    interaction_type = models.IntegerField(choices=interaction_type_choices, default=None)
    committee = models.ForeignKey(Committee, blank=True, null=True, on_delete=models.DO_NOTHING,
                                  verbose_name="Committee / Working Group", related_name="committee_interactions")
    dfo_role = models.IntegerField(choices=ROLE_DFO_CHOICES, default=None,
                                   verbose_name="Role of highest level DFO participant")
    dfo_liaison = models.ManyToManyField(User, blank=True, related_name="interaction_dfo_liaison",
                                         verbose_name=_("DFO liaison/secretariat"))
    other_dfo_participants = models.ManyToManyField(User, blank=True, related_name="interaction_dfo_participants",
                                                    verbose_name=_("Other DFO participants/contributors"))
    external_contact = models.ManyToManyField(ml_models.Person, verbose_name=_("External Contact(s)"),
                                              blank=True, related_name="interaction_ext_contact")
    external_organization = models.ManyToManyField(ml_models.Organization, verbose_name=_("External Organization(s)"),
                                                   blank=True, related_name="interaction_ext_organization")
    date_of_meeting = models.DateTimeField(blank=True, null=True, default=timezone.now,
                                           verbose_name=_("Date of Meeting"))
    main_topic = models.ManyToManyField(DiscussionTopic, blank=True, related_name="main_topics",
                                        verbose_name=_("Main Topic(s) of discussion"))
    species = models.ManyToManyField(Species, blank=True, related_name="species",
                                     verbose_name=_("Main species of discussion"))
    action_items = models.TextField(default="-----", verbose_name=_("Main actions"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("Comments"))
    last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now,
                                         verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
                                         verbose_name=_("last modified by"))

    def __str__(self):
        return "{}: {}".format(self.pk, self.description)


class OrganizationExtension(models.Model):
    organization = models.ForeignKey(ml_models.Organization, blank=False, null=False, default=1, related_name="ext_org",
                                     verbose_name="Organization", on_delete=models.CASCADE)
    associated_provinces = models.ManyToManyField(shared_models.Province, related_name="ext_asc_province",
                                                  verbose_name="Associated Provinces")
    category = models.ManyToManyField(OrgCategory, related_name="ext_org_category", verbose_name="Category")
    area = models.ManyToManyField(Area, related_name="ext_org_area", verbose_name="Area")


class ContactExtension(models.Model):
    contact = models.ForeignKey(ml_models.Person, blank=False, null=False, default=1, related_name="ext_con",
                                verbose_name="Contact", on_delete=models.CASCADE)
    role = models.CharField(max_length=255, default="N/A", verbose_name="Role")

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
