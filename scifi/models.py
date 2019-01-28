from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from lib.functions.fiscal_year import fiscal_year


class AllotmentCode(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name',]

class BusinessLine(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name',]

class LineObject(models.Model):
    code = models.CharField(max_length=50)
    name_eng = models.CharField(max_length=1000)
    description_eng = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.name_eng)

    class Meta:
        ordering = ['code',]

class ResponsibilityCenter(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    responsible_manager = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
                                            related_name="rcs")

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['description',]


class Project(models.Model):
    name = models.CharField(max_length=1000)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    project_lead = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="projects")
    responsibility_center = models.ForeignKey(ResponsibilityCenter, on_delete=models.DO_NOTHING, blank=True, null=True,
                                              related_name='projects')
    default_allotment_code = models.ForeignKey(AllotmentCode, on_delete=models.DO_NOTHING, blank=True, null=True)
    default_business_line = models.ForeignKey(BusinessLine, on_delete=models.DO_NOTHING, blank=True, null=True)
    default_line_object = models.ForeignKey(LineObject, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return "{}".format(self.name)


class Transaction(models.Model):
    # Choices for tranaction_type
    ALLOCATION = 1
    ADJUSTMENT = 2
    TYPE_CHOICES = (
        (ALLOCATION, 'Allocation'),
        (ADJUSTMENT, 'Adjustment'),
    )

    transaction_type = models.IntegerField(default=1, choices=TYPE_CHOICES)
    supplier_description = models.CharField(max_length=1000, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="transactions")

    # should be defaulted once a project is selected
    allotment_code = models.ForeignKey(AllotmentCode, on_delete=models.DO_NOTHING, blank=True, null=True,
                                       related_name='transactions')
    # should be defaulted once a project is selected
    business_line = models.ForeignKey(BusinessLine, on_delete=models.DO_NOTHING, blank=True, null=True,
                                      related_name='transactions')
    # should be defaulted once a project is selected
    line_object = models.ForeignKey(LineObject, on_delete=models.DO_NOTHING, blank=True, null=True,
                                      related_name='transactions')
    requisition_date = models.DateTimeField(blank=True, null=True)
    invoice_date = models.DateTimeField(blank=True, null=True)
    estimated_cost = models.FloatField(blank=True, null=True)
    final_cost = models.FloatField(blank=True, null=True)
    not_in_mrs = models.BooleanField(default=False)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    mrs_notes = models.FloatField(blank=True, null=True)
    procurement_hub_contact = models.CharField(max_length=500, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    fiscal_year = models.CharField(blank=True, null=True, max_length=25)

    def __str__(self):
        return "{}".format(self.supplier_description)

    def save(self, *args, **kwargs):
        if self.invoice_date:
            self.fiscal_year = fiscal_year(date=self.invoice_date)
        super().save(*args, **kwargs)