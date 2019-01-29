from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
import os
import uuid
from django.utils.translation import gettext_lazy as _


class Province(models.Model):
    # Choices for surface_type
    CAN = 'Canada'
    US = 'United States'
    COUNTRY_CHOICES = (
        (CAN, 'Canada'),
        (US, 'United States'),
    )
    name_eng = models.CharField(max_length=1000, blank=True, null=True)
    name_fre = models.CharField(max_length=1000, blank=True, null=True)
    country = models.CharField(max_length=25, choices=COUNTRY_CHOICES)
    abbrev_eng = models.CharField(max_length=25, blank=True, null=True)
    abbrev_fre = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name_eng"))))


class Grouping(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Organization(models.Model):
    name_eng = models.CharField(max_length=1000, blank=True, null=True)
    name_fre = models.CharField(max_length=1000, blank=True, null=True)
    abbrev = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=7, blank=True, null=True)
    province = models.ForeignKey(Province, on_delete=models.DO_NOTHING, blank=True, null=True)
    grouping = models.ManyToManyField(Grouping)

    def __str__(self):
        return "{}".format(self.name_eng)

    class Meta:
        ordering = ['name_eng']


class EntryType(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Status(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class FundingPurpose(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Sector(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Region(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Entry(models.Model):
    # basic
    title = models.CharField(max_length=1000, blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, blank=True, null=True)
    status = models.ForeignKey(Status, default=1, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("status"))
    sector = models.ForeignKey(Sector, on_delete=models.DO_NOTHING, blank=True, null=True)
    entry_type = models.ForeignKey(EntryType, on_delete=models.DO_NOTHING, blank=True, null=True)
    initial_date = models.DateTimeField(blank=True, null=True, verbose_name=_("initial date"))
    leads = models.CharField(max_length=1000, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, blank=True, null=True)

    # funding
    funding_needed = models.NullBooleanField(verbose_name=_("is funding needed?"))
    funding_requested = models.NullBooleanField(verbose_name=_("was funding requested?"))
    amount_expected = models.FloatField(blank=True, null=True, verbose_name=_("How much funding is expected?"))
    transferred = models.NullBooleanField(verbose_name=_("has any funding been transferred?"))
    amount_transferred = models.FloatField(blank=True, null=True, verbose_name=_("If yes, how much funding was transferred?"))
    fiscal_year = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("fiscal year/multiyear"))
    funding_purpose = models.ForeignKey(FundingPurpose, on_delete=models.DO_NOTHING, blank=True, null=True,
                                        verbose_name=_("funding purpose"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now,
                                              verbose_name=_("date last modified"))
    date_created = models.DateTimeField(blank=True, null=True, default=timezone.now,
                                        verbose_name=_("date created"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
                                         verbose_name=_("last modified by"))
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
                                   verbose_name=_("created by"), related_name="user_entries")

    class Meta:
        ordering = ['-date_created', ]

    def __str__(self):
        return "{}".format(self.title)

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('ihub:entry_detail', kwargs={'pk': self.pk})


class EntryNote(models.Model):
    # Choices for type
    ACTION = 1
    NEXTSTEP = 2
    COMMENT = 3
    TYPE_CHOICES = (
        (ACTION, 'Action'),
        (NEXTSTEP, 'Next step'),
        (COMMENT, 'Comment'),
    )

    entry = models.ForeignKey(Entry, related_name='notes', on_delete=models.CASCADE)
    type = models.IntegerField(choices=TYPE_CHOICES)
    date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    note = models.TextField()
    status = models.ForeignKey(Status, default=1, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("status"))

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["-date"]

#
#
# # Create your models here.
#
# class BudgetCode(models.Model):
#     code = models.CharField(max_length=255, blank=True, null=True)
#     name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("name"))
#
#     def __str__(self):
#         return "{} ({})".format(self.code, self.name)
#
#     class Meta:
#         ordering = ['code', ]
#
#
# class Division(models.Model):
#     name = models.CharField(max_length=255)
#     nom = models.CharField(max_length=255, blank=True, null=True)
#
#     def __str__(self):
#         return "{}".format(getattr(self, str(_("name"))))
#
#     class Meta:
#         ordering = ['name', ]
#
#
# class Section(models.Model):
#     name = models.CharField(max_length=255, verbose_name=_("name"))
#     nom = models.CharField(max_length=255, blank=True, null=True)
#     section_head = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
#                                      verbose_name=_("section head"))
#
#     def __str__(self):
#         return "{}".format(getattr(self, str(_("name"))))
#
#     class Meta:
#         ordering = ['name', ]
#
#
# class Program(models.Model):
#     name = models.CharField(max_length=255)
#     nom = models.CharField(max_length=255, blank=True, null=True)
#
#     def __str__(self):
#         return "{}".format(getattr(self, str(_("name"))))
#
#     class Meta:
#         ordering = ['name', ]
#
#
# class Status(models.Model):
#     name = models.CharField(max_length=255)
#     nom = models.CharField(max_length=255, blank=True, null=True)
#
#     def __str__(self):
#         return "{}".format(getattr(self, str(_("name"))))
#
#     class Meta:
#         ordering = ['name', ]
#
#

#
# class EmployeeType(models.Model):
#     # cost_type choices
#     SAL = 1
#     OM = 2
#     COST_TYPE_CHOICES = [
#         (SAL, _("Salary")),
#         (OM, _("O&M")),
#     ]
#
#     name = models.CharField(max_length=255)
#     nom = models.CharField(max_length=255, blank=True, null=True)
#     cost_type = models.IntegerField(choices=COST_TYPE_CHOICES)
#
#     def __str__(self):
#         return "{}".format(getattr(self, str(_("name"))))
#
#
# class Level(models.Model):
#     name = models.CharField(max_length=255)
#
#     def __str__(self):
#         return "{}".format(self.name)
#
#     class Meta:
#         ordering = ['name', ]
#
#
# class Staff(models.Model):
#     # STUDENT_PROGRAM_CHOICES
#     FSWEP = 1
#     COOP = 1
#     STUDENT_PROGRAM_CHOICES = [
#         (FSWEP, "FSWEP"),
#         (COOP, "Coop"),
#     ]
#
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="staff_members",
#                                 verbose_name=_("project"))
#     user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("User"))
#     name = models.CharField(max_length=255, verbose_name=_("Person name (leave blank if user is selected)"), blank=True,
#                             null=True)
#     employee_type = models.ForeignKey(EmployeeType, on_delete=models.DO_NOTHING, verbose_name=_("employee type"))
#     level = models.ForeignKey(Level, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("level"))
#     student_program = models.IntegerField(choices=STUDENT_PROGRAM_CHOICES, blank=True, null=True,
#                                           verbose_name=_("student program"))
#     duration_weeks = models.FloatField(default=0, blank=True, null=True, verbose_name=_("duration in weeks"))
#     overtime_hours = models.FloatField(default=0, blank=True, null=True, verbose_name=_("overtime in hours"))
#     cost = models.FloatField(blank=True, null=True, verbose_name=_("cost"))
#
#     def __str__(self):
#         if self.user:
#             return "{} {}".format(self.user.first_name, self.user.last_name)
#         else:
#             return "{}".format(self.name)
#
#     class Meta:
#         ordering = ['employee_type', 'level']
#
#
# class Collaborator(models.Model):
#     # TYPE_CHOICES
#     COL = 1
#     PAR = 2
#     TYPE_CHOICES = [
#         (COL, _("Collaborator")),
#         (PAR, _("Partner")),
#     ]
#
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="collaborators",
#                                 verbose_name=_("project"))
#     name = models.CharField(max_length=255, verbose_name=_("Name"), blank=True, null=True)
#     type = models.IntegerField(choices=TYPE_CHOICES, verbose_name=_("type"))
#     critical = models.BooleanField(default=True, verbose_name=_("Critical to project delivery"))
#     notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))
#
#     class Meta:
#         ordering = ['name', ]
#
#     def __str__(self):
#         return "{}".format(self.name)
#
#
# class CollaborativeAgreement(models.Model):
#     # NEW_OR_EXISTING_CHOICES
#     NEW = 1
#     EXIST = 2
#     NEW_OR_EXISTING_CHOICES = [
#         (NEW, _("New")),
#         (EXIST, _("Existing")),
#     ]
#
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="agreements", verbose_name=_("project"))
#     partner_organization = models.CharField(max_length=255, blank=True, null=True,
#                                             verbose_name=_("partner organization"))
#     project_lead = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("project lead"))
#     agreement_title = models.CharField(max_length=255, verbose_name=_("Title of the agreement"), blank=True, null=True)
#     new_or_existing = models.IntegerField(choices=NEW_OR_EXISTING_CHOICES, verbose_name=_("new or existing"))
#     notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))
#
#     class Meta:
#         ordering = ['partner_organization', ]
#
#     def __str__(self):
#         return "{}".format(self.partner_organization)
#
#
# class OMCategory(models.Model):
#     # group choices:
#     TRAV = 1
#     EQUIP = 2
#     MAT = 3
#     HR = 4
#     OTH = 5
#     GROUP_CHOICES = (
#         (TRAV, _("Travel")),
#         (EQUIP, _("Equipment Purchase")),
#         (MAT, _("Material and Supplies")),
#         (HR, _("Human Resources")),
#         (OTH, _("Contracts, Leases, Services")),
#     )
#     name = models.CharField(max_length=255, blank=True, null=True)
#     nom = models.CharField(max_length=255, blank=True, null=True)
#     group = models.IntegerField(choices=GROUP_CHOICES)
#
#     class Meta:
#         ordering = ['group', 'name']
#
#     def __str__(self):
#         return "{} ({})".format(getattr(self, str(_("name"))), self.get_group_display())
#
#
# class OMCost(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="om_costs", verbose_name=_("project"))
#     om_category = models.ForeignKey(OMCategory, on_delete=models.DO_NOTHING, related_name="om_costs",
#                                     verbose_name=_("category"))
#     description = models.TextField(blank=True, null=True, verbose_name=_("description"))
#     budget_requested = models.FloatField(default=0, verbose_name=_("budget requested"))
#
#     def __str__(self):
#         return "{}".format(self.om_category)
#
#     class Meta:
#         ordering = ['om_category', ]
#
#
# class CapitalCost(models.Model):
#     # category choices:
#     IMIT = 1
#     LAB = 2
#     FIELD = 3
#     OTH = 4
#     CATEGORY_CHOICES = (
#         (IMIT, _("IM / IT - computers, hardware")),
#         (LAB, _("Lab Equipment")),
#         (FIELD, _("Field Equipment")),
#         (OTH, _("Other")),
#     )
#
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="capital_costs",
#                                 verbose_name=_("project"))
#     category = models.IntegerField(choices=CATEGORY_CHOICES, verbose_name=_("category"))
#     description = models.TextField(blank=True, null=True, verbose_name=_("description"))
#     budget_requested = models.FloatField(default=0, verbose_name=_("budget requested"))
#
#     def __str__(self):
#         return "{}".format(self.get_category_display())
#
#     class Meta:
#         ordering = ['category', ]
#
#
# class GCCost(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="gc_costs", verbose_name=_("project"))
#     recipient_org = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Recipient organization"))
#     project_lead = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("project lead"))
#     proposed_title = models.CharField(max_length=255, blank=True, null=True,
#                                       verbose_name=_("Proposed title of agreement"))
#     gc_program = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Name of G&C program"))
#     budget_requested = models.FloatField(default=0, verbose_name=_("budget requested"))
#
#     def __str__(self):
#         return "{} - {}".format(self.recipient_org, self.gc_program)
#
#     class Meta:
#         ordering = ['recipient_org', ]
