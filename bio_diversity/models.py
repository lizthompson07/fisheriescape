# from django.db import models

# Create your models here.
import os

from django.dispatch import receiver

from shared_models import models as shared_models
from django.db import models
from django.utils.translation import gettext_lazy as _


class BioContainerDet(models.Model):
    class Meta:
        abstract = True

    contdc_id = models.ForeignKey("ContainerDetCode", on_delete=models.DO_NOTHING,
                                  verbose_name=_("Container Detail Code"))
    det_value = models.DecimalField(max_digits=11, decimal_places=5, null=True, blank=True, verbose_name=_("Value"))
    cdsc_id = models.ForeignKey("ContDetSubjCode", on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Container Detail Subject Code"))
    start_date = models.DateField(verbose_name=_("Date detail was recorded"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("Last Date Detail is valid"))
    det_valid = models.BooleanField(default="False", verbose_name=_("Detail still valid?"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))
    created_by = models.CharField(max_length=32, verbose_name=_("Created By"))
    created_date = models.DateField(verbose_name=_("Created Date"))


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


class ContainerDetCode(BioLookup):
    # contdc tag
    min_val = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Minimum Value"))
    max_val = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Maximum Value"))
    unit_id = models.ForeignKey("UnitCode", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Units"))
    cont_subj_flag = models.CharField(max_length=1, verbose_name=_("Container Subject Flag"))


class ContDetSubjCode(BioLookup):
    # cdsc tag
    contdc_id = models.ForeignKey("ContainerDetCode", on_delete=models.DO_NOTHING, verbose_name=_("Container detail code"))


class Cup(BioLookup):
    # cup tag
    pass


class CupDet(BioContainerDet):
    # cupd tag
    cup_id = models.ForeignKey('Cup', on_delete=models.DO_NOTHING, verbose_name=_("Cup"))


class HeathUnit(BioLookup):
    # Heat tag
    manufacturer = models.CharField(max_length=35, verbose_name=_("Maufacturer"))
    inservice_date = models.DateField(verbose_name=_("Date unit was put into service"))
    serial_number = models.CharField(max_length=50, verbose_name=_("Serial Number"))


class HeathUnitDet(BioContainerDet):
    # Heatd tag
    heat_id = models.ForeignKey('HeathUnit', on_delete=models.DO_NOTHING, verbose_name=_("HeathUnit"))


class Instrument(BioModel):
    # inst tag
    instc = models.ForeignKey('InstrumentCode', on_delete=models.DO_NOTHING, verbose_name=_("Instrument Code"))
    serial_number = models.CharField(null=True, blank=True, max_length=250, verbose_name=_("Serial Number"))
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
    # protf_id = models.ForeignKey('Protofile', null=True, blank=True, on_delete=models.DO_NOTHING, verbose_name=_("Protocol File"))
    prot_desc = models.CharField(max_length=4000, verbose_name=_("Protocol Description"))

    def __str__(self):
        return "{}, {}".format(self.protc_id.__str__(), self.prog_id.__str__())


class ProtoCode(BioLookup):
    # protc tag
    pass


def protf_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/bio_diversity/protofiles/<filename>
    return 'bio_diversity/protofiles/{}'.format(filename)


class Protofile(BioModel):
    # protf tag
    prot_id = models.ForeignKey('Protocol', on_delete=models.DO_NOTHING,  related_name="protocol_files", verbose_name=_("Protocol"))

    protf_pdf = models.FileField(upload_to=protf_directory_path, blank=True, null=True, verbose_name=_("Protocol File"))
    # protf_file = models.CharField(max_length=32, verbose_name=_("Protocol File Path"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{}".format(self.protf_pdf)
    pass


@receiver(models.signals.post_delete, sender=Protofile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.protf_pdf:
        if os.path.isfile(instance.protf_pdf.path):
            os.remove(instance.protf_pdf.path)


@receiver(models.signals.pre_save, sender=Protofile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False
    try:
        old_file = Protofile.objects.get(pk=instance.pk).protf_pdf
    except Protofile.DoesNotExist:
        return False
    new_file = instance.protf_pdf
    if old_file and not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class Tank(BioLookup):
    # tank tag
    pass


class TankDet(BioContainerDet):
    # tankd tag
    tank_id = models.ForeignKey('Tank', on_delete=models.DO_NOTHING, verbose_name=_("Tank"))


class Tray(BioLookup):
    # tray tag
    pass


class TrayDet(BioContainerDet):
    # trayd tag
    tray_id = models.ForeignKey('Tray', on_delete=models.DO_NOTHING, verbose_name=_("Tray"))


class Trough(BioLookup):
    # trof tag
    pass


class TroughDet(BioContainerDet):
    # trofd tag
    trof_id = models.ForeignKey('Trough', on_delete=models.DO_NOTHING, verbose_name=_("Trough"))


class UnitCode(BioLookup):
    # unit tag
    pass
