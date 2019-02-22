from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from lib.functions.fiscal_year import fiscal_year
from lib.functions.nz import nz

YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class AllotmentCategory(models.Model):
    name = models.CharField(max_length=25)
    color = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]

class AllotmentCode(models.Model):
    # choices for category
    SAL = "salary"
    CAP = "capital"
    OM = "om"
    GC = "gc"
    CBASE = "cbase"
    CATEGORY_CHOICES = (
        (SAL, "Salary"),
        (CAP, "Capital"),
        (OM, "O&M"),
        (CBASE, "Cbase"),
        (GC, "G&C"),
    )
    code = models.CharField(max_length=50, unique=True)
    name = models.TextField(blank=True, null=True)
    # category = models.CharField(max_length=25, choices=CATEGORY_CHOICES, default="other")
    allotment_category = models.ForeignKey(AllotmentCategory, on_delete=models.DO_NOTHING, related_name="allotment_codes", blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.code, self.name)

    class Meta:
        ordering = ['code', ]


class BusinessLine(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.code, self.name)

    class Meta:
        ordering = ['code', ]


class LineObject(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name_eng = models.CharField(max_length=1000)
    description_eng = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.code, self.name_eng)

    class Meta:
        ordering = ['code', ]


class ResponsibilityCenter(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.TextField(blank=True, null=True)
    responsible_manager = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
                                            related_name="rcs")

    def __str__(self):
        return "{} ({})".format(self.code, self.name)

    class Meta:
        ordering = ['code', ]


class Project(models.Model):
    name = models.CharField(max_length=1000)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    project_lead = models.CharField(max_length=500, blank=True, null=True)
    default_responsibility_center = models.ForeignKey(ResponsibilityCenter, on_delete=models.DO_NOTHING, blank=True,
                                                      null=True, related_name='projects')
    default_allotment_code = models.ForeignKey(AllotmentCode, on_delete=models.DO_NOTHING, blank=True, null=True)
    default_business_line = models.ForeignKey(BusinessLine, on_delete=models.DO_NOTHING, blank=True, null=True)
    default_line_object = models.ForeignKey(LineObject, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.code, self.name)

    class Meta:
        ordering = ['code', ]


class FiscalYear(models.Model):
    full = models.TextField(blank=True, null=True)
    short = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.full)

    class Meta:
        ordering = ['id', ]


class Transaction(models.Model):
    # Choices for transaction_type
    ALLOCATION = 1
    ADJUSTMENT = 2
    EXPENDITURE = 3
    TYPE_CHOICES = (
        (ALLOCATION, 'Allocation'),
        (ADJUSTMENT, 'Adjustment'),
        (EXPENDITURE, 'Expenditure'),
    )

    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, related_name='transactions', verbose_name=_("fiscal year"))
    responsibility_center = models.ForeignKey(ResponsibilityCenter, on_delete=models.DO_NOTHING, related_name='transactions')
    business_line = models.ForeignKey(BusinessLine, on_delete=models.DO_NOTHING, related_name='transactions')
    allotment_code = models.ForeignKey(AllotmentCode, on_delete=models.DO_NOTHING, related_name='transactions')
    line_object = models.ForeignKey(LineObject, on_delete=models.DO_NOTHING, blank=True, null=True,
                                    related_name='transactions')
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name="transactions")
    transaction_type = models.IntegerField(default=1, choices=TYPE_CHOICES)
    supplier_description = models.CharField(max_length=1000, blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    obligation_cost = models.FloatField(blank=True, null=True)
    outstanding_obligation = models.FloatField(blank=True, null=True)
    invoice_cost = models.FloatField(blank=True, null=True)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    invoice_date = models.DateTimeField(blank=True, null=True)
    in_mrs = models.BooleanField(default=True, verbose_name="In MRS", choices=YES_NO_CHOICES)
    amount_paid_in_mrs = models.FloatField(blank=True, null=True, verbose_name="amount paid in MRS")
    mrs_notes = models.CharField(blank=True, null=True, max_length=100, verbose_name="MRS notes")
    procurement_hub_contact = models.CharField(max_length=500, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    exclude_from_rollup = models.BooleanField(default=False, verbose_name="Exclude from rollup", choices=YES_NO_CHOICES)

    def __str__(self):
        return "{}".format(self.supplier_description)

    def save(self, *args, **kwargs):

        if self.obligation_cost:
            self.outstanding_obligation = self.obligation_cost - nz(self.invoice_cost, 0)
        else:
            self.outstanding_obligation = 0
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('scifi:trans_detail', kwargs={'pk': self.id})

    class Meta:
        ordering = ["creation_date", ]
