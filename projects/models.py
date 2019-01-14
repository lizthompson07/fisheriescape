from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
import os
import uuid

# Choices for language
ENG = 1
FRE = 2
LANGUAGE_CHOICES = (
    (ENG, 'English'),
    (FRE, 'French'),
)


# Create your models here.

class BudgetCode(models.Model):
    code = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.code, self.name)

    class Meta:
        ordering = ['code', ]

class Division(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]

class Section(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class Program(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]

class Status(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]

class Project(models.Model):
    fiscal_year = models.CharField(max_length=50, default="2019-2020")

    # basic
    project_title = models.TextField(verbose_name="Title (English)")
    division = models.ForeignKey(Division, on_delete=models.DO_NOTHING, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.DO_NOTHING, blank=True, null=True)
    budget_code = models.ForeignKey(BudgetCode, on_delete=models.DO_NOTHING, related_name="is_section_head_on_projects", blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name="project status")
    approved = models.BooleanField(default=False, verbose_name="Has this project already been approved?")
    start_date = models.DateTimeField(blank=True, null=True, verbose_name="Start Date")
    end_date = models.DateTimeField(blank=True, null=True, verbose_name="End Date")

    # details
    description = models.TextField(blank=True, null=True, verbose_name="Project Objective & Description")
    priorities = models.TextField(blank=True, null=True, verbose_name="Project-specific priorities in 2019/2020")
    deliverables = models.TextField(blank=True, null=True,
                                    verbose_name="Project Deliverables in 2019 / 2020 (bulleted form)")

    # data
    data_collection = models.TextField(blank=True, null=True, verbose_name="What type of data will be collected?")
    data_sharing = models.TextField(blank=True, null=True, verbose_name="Which of these data will be share-worthy and what is the plan to share / disseminate?")
    data_storage = models.TextField(blank=True, null=True, verbose_name="Data Storage / Archiving Plan")
    metadata_url = models.URLField(blank=True, null=True, verbose_name="please provide link to metadata, if available")

    # needs
    regional_dm = models.NullBooleanField(
        verbose_name="Does the program require assistance of the branch data manager?")
    regional_dm_needs = models.TextField(blank=True, null=True,
                                         verbose_name="If yes, please describe")
    sectional_dm = models.NullBooleanField(
        verbose_name="Does the program require assistance of the section's data manager?")
    sectional_dm_needs = models.TextField(blank=True, null=True,
                                          verbose_name="If yes, please describe")
    vehicle_needs = models.TextField(blank=True, null=True,
                                     verbose_name="Describe need for vehicle (type of vehicle, number of weeks, time-frame)")
    it_needs = models.TextField(blank=True, null=True, verbose_name="IT Requirements (software, licenses, hardware)")
    chemical_needs = models.TextField(blank=True, null=True,
                                      verbose_name="Please provide details regarding chemical needs and the plan for storage and disposal.")
    ship_needs = models.TextField(blank=True, null=True, verbose_name="Ship (Coast Guard, Charter) Requirements")

    # admin
    feedback = models.TextField(blank=True, null=True, verbose_name="Do you have any feedback you would like to submit about this process?")
    submitted = models.BooleanField(default=False, verbose_name="Submit project for review")
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        ordering = ['id', ]

    def __str__(self):
        return "{}".format(self.project_title)

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        super().save(*args, **kwargs)


class EmployeeType(models.Model):
    # cost_type choices
    SAL = 1
    OM = 2
    COST_TYPE_CHOICES = [
        (SAL, "Salary"),
        (OM, "O&M"),
    ]

    name = models.CharField(max_length=255)
    cost_type = models.IntegerField(choices=COST_TYPE_CHOICES)

    def __str__(self):
        return "{}".format(self.name)


class Level(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class Staff(models.Model):
    # STUDENT_PROGRAM_CHOICES
    FSWEP = 1
    COOP = 1
    STUDENT_PROGRAM_CHOICES = [
        (FSWEP, "FSWEP"),
        (COOP, "Co-op"),
    ]

    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name="staff_members")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name="User")
    name = models.CharField(max_length=255, verbose_name="Person name (leave blank if user is selected)", blank=True,
                            null=True)
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.DO_NOTHING)
    level = models.ForeignKey(Level, on_delete=models.DO_NOTHING, blank=True, null=True)
    student_program = models.IntegerField(choices=STUDENT_PROGRAM_CHOICES, blank=True, null=True)
    duration_weeks = models.FloatField(default=0, blank=True, null=True)
    overtime_hours = models.FloatField(default=0, blank=True, null=True)
    cost = models.FloatField(blank=True, null=True)

    def __str__(self):
        if self.user:
            return "{} {}".format(self.user.first_name, self.user.last_name)
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['employee_type','level' ]

class Collaborator(models.Model):
    # TYPE_CHOICES
    COL = 1
    PAR = 2
    TYPE_CHOICES = [
        (COL, "Collaborator"),
        (PAR, "Partner"),
    ]

    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name="collaborators")
    name = models.CharField(max_length=255, verbose_name="Name", blank=True,
                            null=True)
    type = models.IntegerField(choices=TYPE_CHOICES)
    critical = models.BooleanField(default=True, verbose_name="Critical to project delivery")
    notes = models.TextField(blank=True, null=True)
