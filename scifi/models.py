import os

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models
from lib.functions.custom_functions import nz

YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


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

    fiscal_year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, related_name='transactions',
                                    verbose_name=_("fiscal year"))
    responsibility_center = models.ForeignKey(shared_models.ResponsibilityCenter, on_delete=models.DO_NOTHING, related_name='transactions')
    business_line = models.ForeignKey(shared_models.BusinessLine, on_delete=models.DO_NOTHING, related_name='transactions')
    allotment_code = models.ForeignKey(shared_models.AllotmentCode, on_delete=models.DO_NOTHING, related_name='transactions')
    line_object = models.ForeignKey(shared_models.LineObject, on_delete=models.DO_NOTHING, blank=True, null=True,
                                    related_name='transactions')
    project = models.ForeignKey(shared_models.Project, on_delete=models.DO_NOTHING, related_name="transactions")
    transaction_type = models.IntegerField(default=3, choices=TYPE_CHOICES)
    supplier_description = models.CharField(max_length=1000, blank=True, null=True)
    expected_purchase_date = models.DateTimeField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    obligation_cost = models.FloatField(blank=True, null=True)
    outstanding_obligation = models.FloatField(blank=True, null=True)
    invoice_cost = models.FloatField(blank=True, null=True)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    consignee_code = models.ForeignKey(shared_models.CosigneeCode, on_delete=models.DO_NOTHING, blank=True, null=True,
                                       related_name='transactions')
    consignee_suffix = models.IntegerField(blank=True, null=True, verbose_name=_("consignee suffix"))
    invoice_date = models.DateTimeField(blank=True, null=True)
    in_mrs = models.BooleanField(default=False, verbose_name="In MRS", choices=YES_NO_CHOICES)
    amount_paid_in_mrs = models.FloatField(blank=True, null=True, verbose_name="amount paid in MRS")
    mrs_notes = models.CharField(blank=True, null=True, max_length=100, verbose_name="MRS notes")
    procurement_hub_contact = models.CharField(max_length=500, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="transactions")
    exclude_from_rollup = models.BooleanField(default=False, verbose_name="Exclude from rollup", choices=YES_NO_CHOICES)

    @property
    def regional_f_number(self):
        if self.consignee_code and self.consignee_suffix:
            return "{}-{}".format(
                self.consignee_code.code,
                self.consignee_suffix,
            )
        elif self.consignee_code:
            return "{}".format(
                self.consignee_code.code,
            )
        else:
            return "n/a"

    def __str__(self):
        return "{}".format(self.supplier_description)

    def save(self, *args, **kwargs):

        if self.obligation_cost:
            self.outstanding_obligation = self.obligation_cost - nz(self.invoice_cost, 0)
        else:
            self.outstanding_obligation = 0

        # if a consignee code was given without a consignee suffix, we should assign a suffix
        # if self.consignee_code and not self.consignee_suffix:
        #     # find the greatest suffix for that code
        #     my_last_trans = Transaction.objects.filter(fiscal_year=self.fiscal_year, consignee_code=self.consignee_code, consignee_suffix__isnull=False).order_by(
        #         "consignee_suffix").last()
        #     if my_last_trans:
        #         my_suffix = my_last_trans.consignee_suffix + 1
        #     else:
        #         my_suffix = "{}0001".format(self.fiscal_year_id[-2:])
        #     self.consignee_suffix = my_suffix

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('scifi:trans_detail', kwargs={'pk': self.id})

    class Meta:
        ordering = ["-creation_date", ]
        unique_together = ["consignee_code", "consignee_suffix"]


class SciFiUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="scifi_users")
    responsibility_centers = models.ManyToManyField(shared_models.ResponsibilityCenter, related_name="scifi_users")

    def __str__(self):
        return "{}".format(self.user)

    class Meta:
        ordering = ["user", ]


class TempFile(models.Model):
    temp_file = models.FileField(upload_to='temp_file')


@receiver(models.signals.post_delete, sender=TempFile)
def auto_delete_region_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.temp_file:
        if os.path.isfile(instance.temp_file.path):
            os.remove(instance.temp_file.path)


@receiver(models.signals.pre_save, sender=TempFile)
def auto_delete_region_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = TempFile.objects.get(pk=instance.pk).temp_file
    except TempFile.DoesNotExist:
        return False

    new_file = instance.temp_file
    if not old_file == new_file and old_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
