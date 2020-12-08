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

    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("End Date"))
    valid = models.BooleanField(default="False", verbose_name=_("Detail still valid?"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))
    created_by = models.CharField(max_length=32, verbose_name=_("Created By"))
    created_date = models.DateField(verbose_name=_("Created Date"))


class AnimalDetCode(BioLookup):
    # anidc tag
    min_val = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Minimum Value"))
    max_val = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Maximum Value"))
    unit_id = models.ForeignKey("UnitCode", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Units"))
    ani_subj_flag = models.BooleanField(verbose_name=_("Subjective?"))


class AniDetSubjCode(BioLookup):
    # ansc tag
    anidc_id = models.ForeignKey("AnimalDetCode", on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Type of measurement"))


class ContainerDetCode(BioLookup):
    # contdc tag
    min_val = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Minimum Value"))
    max_val = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Maximum Value"))
    unit_id = models.ForeignKey("UnitCode", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Units"))
    cont_subj_flag = models.CharField(max_length=1, verbose_name=_("Container Subject Flag"))


class ContDetSubjCode(BioLookup):
    # cdsc tag
    contdc_id = models.ForeignKey("ContainerDetCode", on_delete=models.DO_NOTHING,
                                  verbose_name=_("Container detail code"))


class ContainerXRef(BioModel):
    # Contx tag
    evnt_id = models.ForeignKey("Event", on_delete=models.DO_NOTHING, verbose_name=_("Event"))
    tank_id = models.ForeignKey("Tank", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Tank"))
    trof_id = models.ForeignKey("Trough", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Trough"))
    tray_id = models.ForeignKey("Tray", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Tray"))
    heat_id = models.ForeignKey("HeathUnit", on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Heath Unit"))
    draw_id = models.ForeignKey("Drawer", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Drawer"))
    cup_id = models.ForeignKey("Cup", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Cup"))


class Cup(BioLookup):
    # cup tag
    pass


class CupDet(BioContainerDet):
    # cupd tag
    cup_id = models.ForeignKey('Cup', on_delete=models.DO_NOTHING, verbose_name=_("Cup"))


class Drawer(BioLookup):
    # draw tag
    pass


class EnvCode(BioLookup):
    # envc tag
    min_val = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Minimum Value"))
    max_val = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Maximum Value"))
    unit_id = models.ForeignKey('UnitCode', on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Units"))
    env_subj_flag = models.BooleanField(verbose_name=_("Objective observation?"))


class EnvCondition(BioModel):
    # env tag
    contx_id = models.ForeignKey('ContainerXRef', on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Container Cross Reference"))
    loc_id = models.ForeignKey('Location', on_delete=models.DO_NOTHING, null=True, blank=True,
                               verbose_name=_("Location"))
    inst_id = models.ForeignKey('Instrument', on_delete=models.DO_NOTHING, verbose_name=_("Instrument"))
    envc_id = models.ForeignKey('EnvCode', on_delete=models.DO_NOTHING, verbose_name=_("Environment variable"))
    env_val = models.DecimalField(max_digits=11, decimal_places=5, null=True, blank=True, verbose_name=_("Value"))
    envsc_id = models.ForeignKey('EnvSubjCode', on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Environment Subject Code"))
    env_start = models.DateField(verbose_name=_("Event start date"))
    env_starttime = models.TimeField(null=True, blank=True, verbose_name=_("Event start time"))
    env_end = models.DateField(null=True, blank=True, verbose_name=_("Event end date"))
    env_endtime = models.TimeField(null=True, blank=True, verbose_name=_("Event end time"))
    env_avg = models.BooleanField(default=False,verbose_name=_("Is value an average?"))
    qual_id = models.ForeignKey('QualCode', on_delete=models.DO_NOTHING, verbose_name=_("Quality of observation"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))


class EnvSubjCode(BioLookup):
    # envsc tag
    envc_id = models.ForeignKey('EnvCode', null=True, blank=True, on_delete=models.DO_NOTHING,
                                verbose_name=_("Environment Code"))


class Event(BioModel):
    # evnt tag
    facic_id = models.ForeignKey('FacilityCode', on_delete=models.DO_NOTHING, verbose_name=_("Facility Code"))
    evntc_id = models.ForeignKey('EventCode', on_delete=models.DO_NOTHING, verbose_name=_("Event Code"))
    perc_id = models.ForeignKey('PersonnelCode', on_delete=models.DO_NOTHING, verbose_name=_("Personnel Code"))
    prog_id = models.ForeignKey('Program', on_delete=models.DO_NOTHING, verbose_name=_("Program"))
    team_id = models.ForeignKey('Team', on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Team"))
    evnt_start = models.DateField(verbose_name=_("Event start date"))
    evnt_starttime = models.TimeField(null=True, blank=True, verbose_name=_("Event start time"))
    evnt_end = models.DateField(verbose_name=_("Event end date"))
    evnt_endtime = models.TimeField(null=True, blank=True, verbose_name=_("Event end time"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{}-{}".format(self.prog_id.__str__(), self.evnt_start)

    def save(self, *args, **kwargs):
        self.evnt_starttime = self.evnt_start
        self.evnt_endtime = self.evnt_end

        super().save(*args, **kwargs)


class EventCode(BioLookup):
    # evntc tag
    pass


class FacilityCode(BioLookup):
    # facic tag
    pass


class Feeding(BioModel):
    # feed tag
    contx_id = models.ForeignKey('ContainerXRef', on_delete=models.DO_NOTHING,
                                 verbose_name=_("Container Cross Reference"))
    feedm_id = models.ForeignKey('FeedMethod', on_delete=models.DO_NOTHING, verbose_name=_("Feeding Method"))
    feedc_id = models.ForeignKey('FeedCode', on_delete=models.DO_NOTHING, verbose_name=_("Feeding Code"))
    lot_num = models.CharField(max_length=40, null=True, blank=True, verbose_name=_("Lot Number"))
    amt = models.DecimalField(max_digits=7, decimal_places=3, verbose_name=_("Amount of Feed"))
    unit_id = models.ForeignKey('UnitCode', on_delete=models.DO_NOTHING, verbose_name=_("Units"))
    freq = models.CharField(max_length=40, null=True, blank=True, verbose_name=_("Description of frequency"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{}-{}-{}".format(self.contx_id.__str__(), self.feedc_id.__str__(), self.feedm_id.__str__())


class FeedCode(BioLookup):
    # feedc tag
    manufacturer = models.CharField(max_length=50, verbose_name=_("Maufacturer"))


class FeedMethod(BioLookup):
    # feedm tag
    pass


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


class InstrumentCode(BioLookup):
    # instc tag
    pass


class InstrumentDet(BioTimeModel):
    # instd tag
    inst = models.ForeignKey('Instrument', on_delete=models.DO_NOTHING, verbose_name=_("Instrument"))
    instdc = models.ForeignKey('InstDetCode', on_delete=models.DO_NOTHING, verbose_name=_("Instrument Detail Code"))
    det_value = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Value"))


class InstDetCode(BioLookup):
    # instdc tag
    pass


class Location(BioModel):
    # Loc tag
    evnt_id = models.ForeignKey('Event', on_delete=models.DO_NOTHING, verbose_name=_("Event"))
    locc_id = models.ForeignKey('LocCode', on_delete=models.DO_NOTHING, verbose_name=_("Location Code"))
    rive_id = models.ForeignKey('RiverCode', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("River"))
    trib_id = models.ForeignKey('Tributary', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Tributary"))
    subr_id = models.ForeignKey('SubRiverCode', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("SubRiver Code"))
    relc_id = models.ForeignKey('ReleaseSiteCode', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Release Site Code"))
    loc_lat = models.DecimalField(max_digits=7, decimal_places=5, null=True, blank=True,
                                  verbose_name=_("Lattitude"))
    loc_lon = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True,
                                  verbose_name=_("Longitude"))
    loc_date = models.DateTimeField(verbose_name=_("Date event took place"))
    loc_time = models.TimeField(null=True, blank=True, verbose_name=_("Time event took place"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def save(self, *args, **kwargs):
        self.loc_time = self.loc_date
        super().save(*args, **kwargs)


class LocCode(BioLookup):
    # Locc tag
    pass


class Organization(BioLookup):
    # orga tag
    pass


class PersonnelCode(BioModel):
    # perc tag
    perc_last_name = models.CharField(max_length=32, verbose_name=_("Last Name"))
    perc_first_name = models.CharField(max_length=32, verbose_name=_("First Name"))
    perc_valid = models.BooleanField(default="False", verbose_name=_("Record still valid?"))

    def __str__(self):
        return "{} {}".format(self.perc_first_name, self.perc_last_name)


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


class Protocol(BioTimeModel):
    # prot tag
    prog_id = models.ForeignKey('Program', on_delete=models.DO_NOTHING, verbose_name=_("Program"))
    protc_id = models.ForeignKey('ProtoCode', on_delete=models.DO_NOTHING, verbose_name=_("Protocol Code"))
    protf_id = models.ForeignKey('Protofile', null=True, blank=True, on_delete=models.DO_NOTHING,
                                 verbose_name=_("Protocol File"))
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
    prot_id = models.ForeignKey('Protocol', on_delete=models.DO_NOTHING,  related_name="protocol_files",
                                verbose_name=_("Protocol"))

    protf_pdf = models.FileField(upload_to=protf_directory_path, blank=True, null=True, verbose_name=_("Protocol File"))
    # protf_file = models.CharField(max_length=32, verbose_name=_("Protocol File Path"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{}".format(self.protf_pdf)


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


class QualCode(BioLookup):
    # qual tag
    pass


class ReleaseSiteCode(BioLookup):
    # Relc tag
    rive_id = models.ForeignKey('RiverCode', on_delete=models.DO_NOTHING, verbose_name=_("River"))
    trib_id = models.ForeignKey('Tributary', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Tributary"))
    subr_id =models.ForeignKey('SubRiverCode', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("SubRiver Code"))
    min_lat = models.DecimalField(max_digits=7, decimal_places=5, null=True, blank=True,
                                  verbose_name=_("Min Lattitude"))
    max_lat = models.DecimalField(max_digits=7, decimal_places=5, null=True, blank=True,
                                  verbose_name=_("Max Lattitude"))
    min_lon = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True,
                                  verbose_name=_("Min Longitude"))
    max_lon = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True,
                                  verbose_name=_("Max Longitude"))


class RiverCode(BioLookup):
    # rive tag
    pass


class RoleCode(BioLookup):
    # role tag
    pass


class Sample(BioModel):
    # samp tag
    loc_id = models.ForeignKey('Location', on_delete=models.DO_NOTHING, verbose_name=_("Location"))
    samp_num = models.IntegerField(verbose_name=_("Sample Fish Number"))
    spec_id = models.ForeignKey('SpeciesCode', on_delete=models.DO_NOTHING, verbose_name=_("Species"))
    sampc_id = models.ForeignKey('SampleCode', on_delete=models.DO_NOTHING, verbose_name=_("Sample Code"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))


class SampleCode(BioLookup):
    # sampc tag
    pass


class SampleDet(BioModel):
    samp_id = models.ForeignKey('Sample', on_delete=models.DO_NOTHING, verbose_name=_("Sample"))
    anidc_id = models.ForeignKey('AnimalDetCode', on_delete=models.DO_NOTHING, verbose_name=_("Animal Detail Code"))
    samp_val = models.DecimalField(max_digits=11, decimal_places=5, null=True, blank=True, verbose_name=_("Value"))
    adsc_id = models.ForeignKey('AniDetSubjCode', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Animal Detail SubjectCode"))
    qual_id = models.ForeignKey('QualCode', on_delete=models.DO_NOTHING, verbose_name=_("Quality"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))


class SpeciesCode(BioModel):
    # spec tag
    name = models.CharField(max_length=10, verbose_name=_("Species Name"))
    species = models.CharField(max_length=100, verbose_name=_("Species"))
    com_name = models.CharField(max_length=35, null=True, blank=True, verbose_name=_("Species Common Nme"))


class SubRiverCode(BioLookup):
    # subr tag
    rive_id = models.ForeignKey('RiverCode', on_delete=models.DO_NOTHING, verbose_name=_("River"))
    trib_id = models.ForeignKey('Tributary', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Tributary"))


class Tank(BioLookup):
    # tank tag
    pass


class TankDet(BioContainerDet):
    # tankd tag
    tank_id = models.ForeignKey('Tank', on_delete=models.DO_NOTHING, verbose_name=_("Tank"))


class Team(BioModel):
    # team tag
    perc_id = models.ForeignKey("PersonnelCode", on_delete=models.DO_NOTHING, verbose_name=_("Team Member"))
    role_id = models.ForeignKey("RoleCode", on_delete=models.DO_NOTHING, verbose_name=_("Role Code"))


class Tray(BioLookup):
    # tray tag
    pass


class TrayDet(BioContainerDet):
    # trayd tag
    tray_id = models.ForeignKey('Tray', on_delete=models.DO_NOTHING, verbose_name=_("Tray"))


class Tributary(BioLookup):
    # trib tag
    rive_id = models.ForeignKey('RiverCode', on_delete=models.DO_NOTHING, verbose_name=_("River"))


class Trough(BioLookup):
    # trof tag
    pass


class TroughDet(BioContainerDet):
    # trofd tag
    trof_id = models.ForeignKey('Trough', on_delete=models.DO_NOTHING, verbose_name=_("Trough"))


class UnitCode(BioLookup):
    # unit tag
    pass
