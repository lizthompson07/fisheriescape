#from django.db import models

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


class BioTimeModel(models.Model):
    # model with start date/end date, still valid, created by and created date fields
    class Meta:
        abstract = True

    start_date = models.DateField(verbose_name=_("Date of change"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("Last Date Change is valid"))
    valid = models.BooleanField(default="False", verbose_name=_("Detail still valid?"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))
    created_by = models.CharField(max_length=32, verbose_name=_("Created By"))
    created_date = models.DateField(verbose_name=_("Created Date"))


class Instrument(BioModel):
    # inst tag
    instc = models.ForeignKey('InstrumentCode', on_delete=models.DO_NOTHING, verbose_name=_("Instrument Code"))
    serial_number = models.CharField(null=True, max_length=250, verbose_name=_("Serial Number"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{} - {}".format(self.instc.__str__(), self.serial_number)
    pass


class InstrumentCode(BioLookup):
    # instc tag
    pass


class InstrumentDet(BioTimeModel):
    # instd tag
    inst = models.ForeignKey('Instrument', on_delete=models.DO_NOTHING, verbose_name=_("Instrument"))
    instdc = models.ForeignKey('InstDetCode', on_delete=models.DO_NOTHING, verbose_name=_("Instrument Detail Code"))
    det_value = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Value"))
    pass


class InstDetCode(BioLookup):
    # instdc tag
    pass


class Organization(BioLookup):
    # orga tag
    pass


class Program(BioTimeModel):
    # prog tag
    prog_name = models.CharField(max_length=30, verbose_name=_("Program Name"))
    prog_desc = models.CharField(max_length=4000, verbose_name=_("Program Description"))
    proga_id = models.ForeignKey('ProgAuthority', on_delete=models.DO_NOTHING, verbose_name=_("Program Authority"))
    orga_id = models.ForeignKey('Organization', on_delete=models.DO_NOTHING, verbose_name=_("Organization"))

    def __str__(self):
        return self.prog_name


class ProgAuthority(BioModel):
    # proga tag
    proga_last_name = models.CharField(max_length=32, verbose_name=_("Last Name"))
    proga_first_name = models.CharField(max_length=32, verbose_name=_("First Name"))

    def __str__(self):
        return "{} {}".format(self.proga_first_name, self.proga_last_name)
    pass


class Protocol(BioTimeModel):
    # prot tag
    prog_id = models.ForeignKey('Program', on_delete=models.DO_NOTHING, verbose_name=_("Program"))
    protc_id = models.ForeignKey('ProtoCode', on_delete=models.DO_NOTHING, verbose_name=_("Protocol Code"))
    protf_id = models.ForeignKey('Protofile', on_delete=models.DO_NOTHING, verbose_name=_("Protocol File"))
    prot_desc = models.CharField(max_length=4000, verbose_name=_("Protocol Description"))

    def __str__(self):
        return "{}-{}".format(self.protc_id.__str__(), self.prog_id.__str__())



class ProtoCode(BioLookup):
    # protc tag
    pass


class Protofile(BioModel):
    # protf tag
    prot_id = models.IntegerField(verbose_name=_("Protocol Id"))
    protf_file = models.CharField(max_length=32, verbose_name=_("Protocol File Path"))
    # models.FilePathField(path='', verbose_name=_("Protocol File"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))
    pass
