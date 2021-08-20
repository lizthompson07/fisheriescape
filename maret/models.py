from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from masterlist import models as ml_models

from shared_models import models as shared_models
from shared_models.utils import get_metadata_string

from lib.functions.custom_functions import listrify
from lib.functions.custom_functions import nz

NULL_YES_NO_CHOICES = (
    (None, _("---------")),
    (1, _("Yes")),
    (0, _("No")),
)


class EntryType(shared_models.SimpleLookup):
    color = models.CharField(max_length=25, blank=True, null=True)


class Status(shared_models.SimpleLookup):
    color = models.CharField(max_length=25, blank=True, null=True)


class FundingPurpose(shared_models.SimpleLookup):
    pass


class FundingProgram(shared_models.SimpleLookup):

    abbrev_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("abbreviation (English)"))
    abbrev_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("abbreviation (French)"))

    @property
    def full_eng(self):
        return "{} ({})".format(self.name, self.abbrev_eng)

    @property
    def full_fre(self):
        return "{} ({})".format(self.nom, self.abbrev_fre)


class Entry(models.Model):
    # basic
    title = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("title"))
    location = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("location"))
    proponent = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("proponent"))
    organizations = models.ManyToManyField(ml_models.Organization, related_name="entries", verbose_name=_("organizations"))
    initial_date = models.DateTimeField(verbose_name=_("initial activity date"), blank=True, null=True)
    response_requested_by = models.DateTimeField(verbose_name=_("response requested by"), blank=True, null=True)
    anticipated_end_date = models.DateTimeField(verbose_name=_("anticipated end date"), blank=True, null=True)
    is_faa_required = models.BooleanField(null=True, blank=True, verbose_name=_("is an FAA required?"))
    status = models.ForeignKey(Status, default=1, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("status"),
                               related_name="entries")
    sectors = models.ManyToManyField(ml_models.Sector, related_name="entries", verbose_name=_("DFO sectors"))
    entry_type = models.ForeignKey(EntryType, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="entries",
                                   verbose_name=_("Entry Type"))  # title case needed
    regions = models.ManyToManyField(shared_models.Region, related_name="entries", verbose_name=_("regions"))
    response_deadline = models.DateTimeField(verbose_name=_("response deadline"), blank=True, null=True)

    # funding
    funding_program = models.ForeignKey(FundingProgram, on_delete=models.DO_NOTHING, blank=True, null=True,
                                        verbose_name=_("funding program"), related_name="entries")
    fiscal_year = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("fiscal year/multiyear"))
    funding_needed = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES, verbose_name=_("is funding needed?"))
    funding_purpose = models.ForeignKey(FundingPurpose, on_delete=models.DO_NOTHING, blank=True, null=True,
                                        verbose_name=_("funding purpose"), related_name="entries")
    amount_requested = models.FloatField(blank=True, null=True, verbose_name=_("funding requested"))  # title case needed
    amount_approved = models.FloatField(blank=True, null=True, verbose_name=_("funding approved"))
    amount_transferred = models.FloatField(blank=True, null=True, verbose_name=_("amount transferred"))
    amount_lapsed = models.FloatField(blank=True, null=True, verbose_name=_("amount lapsed"))
    amount_owing = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES,
                                       verbose_name=_("does any funding need to be recovered?"))

    # meta
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    date_created = models.DateTimeField(default=timezone.now, verbose_name=_("date created"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("created by"),
                                   related_name="user_entries")
    old_id = models.IntegerField(blank=True, null=True, editable=False, unique=True)  # used for importing new data.

    @property
    def has_funding_detail(self):
        return self.funding_program or self.fiscal_year or self.funding_needed or \
               self.funding_purpose or self.amount_requested or self.amount_approved or \
               self.amount_transferred or self.amount_lapsed or self.amount_owing

    class Meta:
        ordering = ['-date_created', ]

    def __str__(self):
        return "{}".format(self.title)

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        # self.fiscal_year = fiscal_year(date=self.initial_date)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('ihub:entry_detail', kwargs={'pk': self.pk})

    @property
    def amount_outstanding(self):
        return nz(self.amount_approved, 0) - nz(self.amount_transferred, 0) - nz(self.amount_lapsed, 0)

    @property
    def followups(self):
        return self.notes.filter(type=4)

    @property
    def other_notes(self):
        return self.notes.filter(~Q(type__in=[4]))

    @property
    def orgs_str(self):
        return listrify([org for org in self.organizations.all()])

    @property
    def sectors_str(self):
        return listrify([sec for sec in self.sectors.all()])

    @property
    def metadata(self):
        return get_metadata_string(
            self.date_created,
            self.created_by,
            self.date_last_modified,
            self.last_modified_by,
        )
