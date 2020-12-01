from django.db import models

# Create your models here.
from shared_models import models as shared_models
from django.db import models
from django.utils.translation import gettext_lazy as _


class BioLookup(shared_models.Lookup):
    class Meta:
        abstract = True

    created_by = models.CharField(max_length=32, verbose_name=_("Created By"))
    created_date = models.DateField(verbose_name=_("Created Date"))


class BioModel(models.Model):
    # normal model with created by and created date fields
    class Meta:
        abstract = True

    created_by = models.CharField(max_length=32, verbose_name=_("Created By"))
    created_date = models.DateField(verbose_name=_("Created Date"))


class Instrument(BioModel):
    # inst tag
    instc = models.ForeignKey('InstrumentCode', on_delete=models.DO_NOTHING, verbose_name=_("Instrument Code"),
                              related_name="instrument_code")
    serial_number = models.CharField(null=True, max_length=250, verbose_name=_("Serial Number"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))
    pass


class InstrumentCode(BioLookup):
    # instc tag
    pass


class InstrumentDet(BioModel):
    # instd tag
    inst = models.ForeignKey('Instrument', on_delete=models.DO_NOTHING, verbose_name=_("Instrument"),
                             related_name="inst")
    instdc = models.ForeignKey('InstDetCode', on_delete=models.DO_NOTHING, verbose_name=_("Instrument Detail Code"),
                               related_name="inst_det_code")
    det_value = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Value"))
    start_date = models.DateField(verbose_name=_("Date of change"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("Last Date Change is valid"))
    valid = models.BooleanField(default="False", verbose_name=_("Detail still valid?"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))
    pass


class InstDetCode(BioLookup):
    # instdc tag
    pass


class Organization(BioLookup):
    # orga tag
    pass


class ProgAuthority(BioModel):
    # proga tag
    proga_last_name = models.CharField(max_length=32, verbose_name=_("Last Name"))
    proga_first_name = models.CharField(max_length=32, verbose_name=_("First Name"))
    pass


class ProtoCode(BioLookup):
    # protc tag
    pass


class Protofile(BioModel):
    # protf tag
    prot_id = models.IntegerField(verbose_name=_("Protocol Id"))
    protf_file = models.CharField(max_length=32, verbose_name=_("Protocol File Path"))  # models.FilePathField(path='', verbose_name=_("Protocol File"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))
    pass
