# from django.db import models

# Create your models here.
import os
import csv
from datetime import datetime
from io import StringIO
import pandas as pd
from django.core.exceptions import ValidationError
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
                                verbose_name=_("Container Detail Subjective Code"))
    start_date = models.DateField(verbose_name=_("Date detail was recorded"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("Last Date Detail is valid"))
    det_valid = models.BooleanField(default="False", verbose_name=_("Detail still valid?"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))
    created_by = models.CharField(max_length=32, verbose_name=_("Created By"))
    created_date = models.DateField(verbose_name=_("Created Date"))

    def clean(self):
        if self.det_value > self.contdc_id.max_val or self.det_value < self.contdc_id.min_val:
            raise ValidationError({
                "det_value": ValidationError("Value {} exceeds limits. Max: {}, Min: {}".format(self.det_value,
                                                                                                self.contdc_id.max_val,
                                                                                                self.contdc_id.min_val))
            })


class BioDet(models.Model):
    class Meta:
        abstract = True

    det_val = models.DecimalField(max_digits=11, decimal_places=5, null=True, blank=True, verbose_name=_("Value"))
    qual_id = models.ForeignKey('QualCode', on_delete=models.DO_NOTHING, verbose_name=_("Quality"))
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
    valid = models.BooleanField(default="True", verbose_name=_("Detail still valid?"))
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


class AniDetailXref(BioModel):
    # anix tag
    evnt_id = models.ForeignKey("Event", on_delete=models.DO_NOTHING, verbose_name=_("Event"),
                                related_name="animal_details")
    contx_id = models.ForeignKey("ContainerXRef", on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Container Cross Reference"))
    loc_id = models.ForeignKey("Location", on_delete=models.DO_NOTHING, null=True, blank=True,
                               verbose_name=_("Location"))
    indvt_id = models.ForeignKey("IndTreatment", on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Individual Treatment"))
    indv_id = models.ForeignKey("Individual", on_delete=models.DO_NOTHING, null=True, blank=True,
                                related_name="animal_details", verbose_name=_("Individual"))
    spwn_id = models.ForeignKey("Spawning", on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Spawning"))
    grp_id = models.ForeignKey("Group", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Group"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['evnt_id', 'contx_id', 'loc_id', 'indvt_id', 'indv_id', 'spwn_id',
                                            'grp_id'], name='Animal Detail Cross Reference Uniqueness ')
        ]

    def clean(self):
        if not (self.contx_id or self.loc_id or self.indvt_id or self.indv_id or self.spwn_id or self.grp_id):
            raise ValidationError("You must specify at least one item to reference to the event")

    def __str__(self):
        return "Ani X Ref for {}".format(self.evnt_id.__str__())


class Collection(BioLookup):
    # coll tag
    pass


class ContainerDetCode(BioLookup):
    # contdc tag
    min_val = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Minimum Value"))
    max_val = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Maximum Value"))
    unit_id = models.ForeignKey("UnitCode", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Units"))
    cont_subj_flag = models.BooleanField(verbose_name=_("Subjective detail?"))


class ContDetSubjCode(BioLookup):
    # cdsc tag
    contdc_id = models.ForeignKey("ContainerDetCode", on_delete=models.DO_NOTHING,
                                  verbose_name=_("Container detail code"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'contdc_id'], name='CDSC Uniqueness')
        ]


class ContainerXRef(BioModel):
    # contx tag
    evnt_id = models.ForeignKey("Event", on_delete=models.DO_NOTHING, verbose_name=_("Event"),
                                related_name="containers")
    tank_id = models.ForeignKey("Tank", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Tank"))
    trof_id = models.ForeignKey("Trough", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Trough"))
    tray_id = models.ForeignKey("Tray", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Tray"))
    heat_id = models.ForeignKey("HeathUnit", on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Heath Unit"))
    draw_id = models.ForeignKey("Drawer", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Drawer"))
    cup_id = models.ForeignKey("Cup", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Cup"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['evnt_id', 'tank_id', 'trof_id', 'tray_id', 'heat_id', 'draw_id', 'cup_id'],
                                    name='Container Cross Reference Uniqueness')
        ]

    def __str__(self):
        return "Container X Ref for {}".format(self.evnt_id.__str__())

    def clean(self):
        if not (self.tank_id or self.tray_id or self.trof_id or self.heat_id or self.draw_id or self.cup_id):
            raise ValidationError("You must specify at least one container to reference to the event")


class Count(BioModel):
    # cnt tag
    loc_id = models.ForeignKey("Location", on_delete=models.DO_NOTHING, verbose_name=_("Location"))
    contx_id = models.ForeignKey("ContainerXRef", on_delete=models.DO_NOTHING,
                                 verbose_name=_("Container Cross Reference"))
    cntc_id = models.ForeignKey("CountCode", on_delete=models.DO_NOTHING, verbose_name=_("Count Code"))
    spec_id = models.ForeignKey("SpeciesCode", on_delete=models.DO_NOTHING, verbose_name=_("Species"))
    cnt = models.DecimalField(max_digits=6, decimal_places=0, verbose_name=_("Count"))
    est = models.BooleanField(verbose_name=_("Estimated?"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['loc_id', 'contx_id', 'cntc_id', 'spec_id'], name='Count Uniqueness')
        ]

    def __str__(self):
        return "{}-{}-{}".format(self.loc_id.__str__(), self.spec_id.__str__(), self.cntc_id.__str__())


class CountCode(BioLookup):
    # cntc tag
    pass


class CountDet(BioDet):
    # cntd tag
    cnt_id = models.ForeignKey("Count", on_delete=models.DO_NOTHING, verbose_name=_("Count"))
    anidc_id = models.ForeignKey('AnimalDetCode', on_delete=models.DO_NOTHING, verbose_name=_("Animal Detail Code"))
    adsc_id = models.ForeignKey('AniDetSubjCode', on_delete=models.DO_NOTHING,
                                verbose_name=_("Animal Detail Subjective Code"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cnt_id', 'anidc_id', 'adsc_id'], name='Count Detail Uniqueness')
        ]

    def __str__(self):
        return "{} - {}".format(self.cnt_id.__str__(), self.anidc_id.__str__())

    def clean(self):
        if self.det_val > self.anidc_id.max_val or self.det_val < self.anidc_id.min_val:
            raise ValidationError({
                "det_val": ValidationError("Value {} exceeds limits. Max: {}, Min: {}".format(self.det_val,
                                                                                              self.anidc_id.max_val,
                                                                                              self.anidc_id.min_val))
            })


class Cup(BioLookup):
    # cup tag
    pass


class CupDet(BioContainerDet):
    # cupd tag
    cup_id = models.ForeignKey('Cup', on_delete=models.DO_NOTHING, verbose_name=_("Cup"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cup_id', 'contdc_id', 'cdsc_id', 'start_date'],
                                    name='Cup Detail Uniqueness')
        ]

    def __str__(self):
        return "{} - {}".format(self.cup_id.__str__(), self.contdc_id.__str__())


class DataLoader(BioModel):
    # data tag
    evnt_id = models.ForeignKey('Event', on_delete=models.DO_NOTHING, verbose_name=_("Event"))
    evntc_id = models.ForeignKey('EventCode', on_delete=models.DO_NOTHING, verbose_name=_("Data Format"))
    data_csv = models.FileField(upload_to="", null=True, blank=True, verbose_name=_("Datafile"))

    def save(self, *args, **kwargs):
        try:
            data = pd.read_excel(self.data_csv, engine='openpyxl')
        except:
            raise Exception("File format not valid")
        if self.evntc_id.__str__() == "Electrofishing":
            loc = Location(evnt_id_id=self.evnt_id.pk,
                           locc_id_id=1,
                           rive_id=RiverCode.objects.filter(name=data["River"][0]).get(),
                           subr_id=SubRiverCode.objects.filter(name__iexact=data["Branch"][0]).get(),
                           relc_id=ReleaseSiteCode.objects.filter(name__iexact=data["Site"][0]).get(),
                           loc_date=datetime.strptime(data["Date"][0], "%Y-%b-%d"),
                           comments=data["Comments"][0],
                           created_by=self.created_by,
                           created_date=self.created_date,
                           )
            try:
                loc.save()
            except:
                pass
            envc=EnvCondition(loc_id_id=loc.pk,
                              inst_id=Instrument.objects.first(),
                              envc_id=EnvCode.objects.filter(name__iexact="Temperature").get(),
                              env_val=data["temp"][0],
                              env_start=datetime.strptime(data["Date"][0], "%Y-%b-%d"),
                              env_avg=False,
                              qual_id=QualCode.objects.filter(name="Good").get(),
                              created_by=self.created_by,
                              created_date=self.created_date,
                              )
            envc.save()
            grp = Group(spec_id=SpeciesCode.objects.filter(name__iexact="Salmon").get(),
                        stok_id=StockCode.objects.filter(name=data["River"][0]).get(),
                        coll_id=Collection.objects.filter(name__icontains=data["purpose"][0][:8]).get(),
                        grp_valid=True,
                        created_by=self.created_by,
                        created_date=self.created_date, 
                        )
            grp.save()
            anix=AniDetailXref(evnt_id_id=self.evnt_id.pk,
                               grp_id_id=grp.pk,
                               created_by=self.created_by,
                               created_date=self.created_date,
                               )
            anix.save()
            grpd = GroupDet(anix_id_id=anix.pk,
                            anidc_id=AnimalDetCode.objects.filter(name__iexact="Number of Fish").get(),
                            det_val=data["# of salmon observed/collected"].sum(),
                            qual_id=QualCode.objects.filter(name="Good").get(),
                            # det_val=True,
                            created_by=self.created_by,
                            created_date=self.created_date,
                            )
            grpd.save()
        return super().save(*args, **kwargs)


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
                               verbose_name=_("Location"), related_name="env_condition")
    inst_id = models.ForeignKey('Instrument', on_delete=models.DO_NOTHING, verbose_name=_("Instrument"))
    envc_id = models.ForeignKey('EnvCode', on_delete=models.DO_NOTHING, verbose_name=_("Environment variable"))
    env_val = models.DecimalField(max_digits=11, decimal_places=5, null=True, blank=True, verbose_name=_("Value"))
    envsc_id = models.ForeignKey('EnvSubjCode', on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Environment Subjective Code"))
    env_start = models.DateTimeField(verbose_name=_("Event start date"))
    env_end = models.DateTimeField(null=True, blank=True, verbose_name=_("Event end date"))
    env_avg = models.BooleanField(default=False, verbose_name=_("Is value an average?"))
    qual_id = models.ForeignKey('QualCode', on_delete=models.DO_NOTHING, verbose_name=_("Quality of observation"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['contx_id', 'loc_id', 'inst_id'], name='Environment Condition Uniqueness')
        ]

    def __str__(self):
        if self.contx_id:
            return "{}-{}".format(self.contx_id.__str__(), self.envc_id.__str__())
        elif self.loc_id:
            return "{}-{}".format(self.loc_id.__str__(), self.envc_id.__str__())
        else:
            return "{}-{}".format(self.envc_id.__str__(), self.env_start)

    def clean(self):
        if self.env_val > self.envc_id.max_val or self.env_val < self.envc_id.min_val:
            raise ValidationError({
                "env_val": ValidationError("Value {} exceeds limits. Max: {}, Min: {}".format(self.env_val,
                                                                                              self.envc_id.max_val,
                                                                                              self.envc_id.min_val))
            })


def envcf_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/bio_diversity/env_conditions/<filename>
    return 'bio_diversity/env_conditions/{}'.format(filename)


class EnvCondFile(BioModel):
    # envcf tag
    env_id = models.OneToOneField("EnvCondition", on_delete=models.DO_NOTHING, verbose_name=_("Environment Condition"),
                                  related_name="envcf_id")
    env_pdf = models.FileField(upload_to=envcf_directory_path, null=True, blank=True,
                               verbose_name=_("Environment Condition File"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{}".format(self.env_pdf)


@receiver(models.signals.post_delete, sender=EnvCondFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.env_pdf:
        if os.path.isfile(instance.env_pdf.path):
            os.remove(instance.env_pdf.path)


@receiver(models.signals.pre_save, sender=EnvCondFile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False
    try:
        old_file = EnvCondFile.objects.get(pk=instance.pk).env_pdf
    except EnvCondFile.DoesNotExist:
        return False
    new_file = instance.env_pdf
    if old_file and not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class EnvSubjCode(BioLookup):
    # envsc tag
    envc_id = models.ForeignKey('EnvCode', null=True, blank=True, on_delete=models.DO_NOTHING,
                                verbose_name=_("Environment Code"))


class EnvTreatCode(BioLookup):
    # envtc tag
    rec_dose = models.CharField(max_length=400, verbose_name=_("Recommended Dosage"))
    manufacturer = models.CharField(max_length=50, verbose_name=_("Treatment Manufacturer"))


class EnvTreatment(BioModel):
    # envt tag
    contx_id = models.ForeignKey('ContainerXRef', on_delete=models.DO_NOTHING,
                                 verbose_name=_("Container Cross Reference"))
    envtc_id = models.ForeignKey('EnvTreatCode', on_delete=models.DO_NOTHING,
                                 verbose_name=_("Environment Treatment Code"))
    lot_num = models.CharField(max_length=30, verbose_name=_("Lot Number"))
    amt = models.DecimalField(max_digits=7, decimal_places=3, verbose_name=_("Dose"))
    unit_id = models.ForeignKey('UnitCode', on_delete=models.DO_NOTHING, verbose_name=_("Units"))
    duration = models.DecimalField(max_digits=5, decimal_places=0, verbose_name=_("Duration (minutes)"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{}-{}".format(self.contx_id.__str__(), self.envtc_id.__str__())

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['contx_id', 'envtc_id'], name='Environment Treatment Uniqueness')
        ]


class Event(BioModel):
    # evnt tag
    facic_id = models.ForeignKey('FacilityCode', on_delete=models.DO_NOTHING, verbose_name=_("Facility Code"))
    evntc_id = models.ForeignKey('EventCode', on_delete=models.DO_NOTHING, verbose_name=_("Event Code"))
    perc_id = models.ForeignKey('PersonnelCode', on_delete=models.DO_NOTHING, verbose_name=_("Personnel Code"),
                                limit_choices_to={'perc_valid': True})
    prog_id = models.ForeignKey('Program', on_delete=models.DO_NOTHING, verbose_name=_("Program"),
                                limit_choices_to={'valid': True})
    team_id = models.ForeignKey('Team', on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Team"))
    evnt_start = models.DateTimeField(verbose_name=_("Event start date"))
    evnt_end = models.DateTimeField(null=True, blank=True, verbose_name=_("Event end date"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{}-{}-{}".format(self.prog_id.__str__(), self.evntc_id.__str__(), self.evnt_start.date())

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['facic_id', 'evntc_id', 'prog_id', 'evnt_start', 'evnt_end'],
                                    name='Event Uniqueness')
        ]


class EventCode(BioLookup):
    # evntc tag
    pass


class FacilityCode(BioLookup):
    # facic tag
    pass


class Fecundity(BioTimeModel):
    # fecu tag
    stok_id = models.ForeignKey('StockCode', on_delete=models.DO_NOTHING, verbose_name=_("Stock Code"))
    coll_id = models.ForeignKey('Collection', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Collection"))
    alpha = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_("A"))
    beta = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_("B"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['stok_id', 'coll_id', 'start_date'], name='Fecundity Uniqueness')
        ]

    def __str__(self):
        return "{}-{}-{}".format(self.stok_id.__str__(), self.alpha, self.beta)


class Feeding(BioModel):
    # feed tag
    contx_id = models.OneToOneField('ContainerXRef', unique=True, on_delete=models.DO_NOTHING,
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


class Group(BioModel):
    # grp tag
    frm_grp_id = models.ForeignKey('Group', on_delete=models.DO_NOTHING, null=True, blank=True,
                                   verbose_name=_("From Parent Group"))
    spec_id = models.ForeignKey('SpeciesCode', on_delete=models.DO_NOTHING, verbose_name=_("Species"))
    stok_id = models.ForeignKey('StockCode', on_delete=models.DO_NOTHING, verbose_name=_("Stock Code"))
    coll_id = models.ForeignKey('Collection', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Collection"))
    grp_valid = models.BooleanField(default="True", verbose_name=_("Group still valid?"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{}-{} group".format(self.spec_id.__str__(), self.stok_id.__str__())


class GroupDet(BioDet):
    # grpd tag
    anix_id = models.ForeignKey('AniDetailXRef', on_delete=models.DO_NOTHING,
                                verbose_name=_("Animal Detail Cross Reference"))
    anidc_id = models.ForeignKey('AnimalDetCode', on_delete=models.DO_NOTHING, verbose_name=_("Animal Detail Code"))
    adsc_id = models.ForeignKey('AniDetSubjCode', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Animal Detail Subjective Code"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['anix_id', 'anidc_id', 'adsc_id'], name='Group Detail Uniqueness')
        ]

    def __str__(self):
        return "{} - {}".format(self.anix_id.__str__(), self.anidc_id.__str__())

    def clean(self):
        if self.det_val > self.anidc_id.max_val or self.det_val < self.anidc_id.min_val:
            raise ValidationError({
                "det_val": ValidationError("Value {} exceeds limits. Max: {}, Min: {}".format(self.det_val,
                                                                                              self.anidc_id.max_val,
                                                                                              self.anidc_id.min_val))
            })


class HeathUnit(BioLookup):
    # Heat tag
    manufacturer = models.CharField(max_length=35, verbose_name=_("Maufacturer"))
    inservice_date = models.DateField(verbose_name=_("Date unit was put into service"))
    serial_number = models.CharField(max_length=50, verbose_name=_("Serial Number"))


class HeathUnitDet(BioContainerDet):
    # Heatd tag
    heat_id = models.ForeignKey('HeathUnit', on_delete=models.DO_NOTHING, verbose_name=_("Heath Unit"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['heat_id', 'contdc_id', 'cdsc_id', 'start_date'],
                                    name='Heath Unit Detail Uniqueness')
        ]

    def __str__(self):
        return "{} - {}".format(self.heat_id.__str__(), self.contdc_id.__str__())


def img_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/bio_diversity/images/<filename>
    return 'bio_diversity/images/{}'.format(filename)


class Image(BioModel):
    # img tag
    imgc_id = models.ForeignKey("ImageCode", on_delete=models.DO_NOTHING, verbose_name=_("Image Code"))
    loc_id = models.ForeignKey("Location", on_delete=models.DO_NOTHING, null=True, blank=True,
                               verbose_name=_("Location"))
    cntd_id = models.ForeignKey("CountDet", on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Count Detail"))
    grpd_id = models.ForeignKey("GroupDet", on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Group Detail"))
    sampd_id = models.ForeignKey("SampleDet", on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Sample Detail"))
    indvd_id = models.ForeignKey("IndividualDet", on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Individual Detail"))
    spwnd_id = models.ForeignKey("SpawnDet", on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Spawn Detail"))
    tankd_id = models.ForeignKey("TankDet", on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Tank Detail"))
    heatd_id = models.ForeignKey("HeathUnitDet", on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Heath Unit Detail"))
    draw_id = models.ForeignKey("Drawer", on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Drawer"))
    trofd_id = models.ForeignKey("TroughDet", on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Trough Detail"))
    trayd_id = models.ForeignKey("TrayDet", on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("Tray Detail"))
    cupd_id = models.ForeignKey("CupDet", on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Cup Detail"))
    img_png = models.FileField(upload_to=img_directory_path, null=True, blank=True, verbose_name=_("Image File"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{}".format(self.img_png)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["imgc_id", "loc_id", "cntd_id", "grpd_id", "sampd_id", "indvd_id",
                                            "spwnd_id", "tankd_id", "heatd_id", "draw_id", "trofd_id", "trayd_id",
                                            "cupd_id"], name='Image Uniqueness')
        ]


@receiver(models.signals.post_delete, sender=Image)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.img_png:
        if os.path.isfile(instance.img_png.path):
            os.remove(instance.img_png.path)


@receiver(models.signals.pre_save, sender=Image)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False
    try:
        old_file = Image.objects.get(pk=instance.pk).img_png
    except Image.DoesNotExist:
        return False
    new_file = instance.img_png
    if old_file and not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class ImageCode(BioLookup):
    # imgc tag
    pass


class Individual(BioModel):
    # indv tag

    grp_id = models.ForeignKey('Group', on_delete=models.DO_NOTHING, null=True, blank=True,
                               verbose_name=_("From Parent Group"), limit_choices_to={'grp_valid': True})
    spec_id = models.ForeignKey('SpeciesCode', on_delete=models.DO_NOTHING, verbose_name=_("Species"))
    stok_id = models.ForeignKey('StockCode', on_delete=models.DO_NOTHING, verbose_name=_("Stock Code"))
    coll_id = models.ForeignKey('Collection', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Collection"))
    # ufid = unique FISH id
    ufid = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name=_("ABL Fish UFID"))
    pit_tag = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name=_("PIT tag ID"))
    indv_valid = models.BooleanField(default="True", verbose_name=_("Entry still valid?"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        if self.ufid:
            return "{}".format(self.ufid)
        elif self.pit_tag:
            return "{}".format(self.pit_tag)
        else:
            return "Non Id'd {} from {}".format(self.spec_id.__str__(), self.stok_id.__str__())


class IndividualDet(BioDet):
    # indvd tag
    anix_id = models.ForeignKey('AniDetailXRef', on_delete=models.DO_NOTHING,
                                verbose_name=_("Animal Detail Cross Reference"))
    anidc_id = models.ForeignKey('AnimalDetCode', on_delete=models.DO_NOTHING, verbose_name=_("Animal Detail Code"))
    adsc_id = models.ForeignKey('AniDetSubjCode', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Animal Detail Subjective Code"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['anix_id', 'anidc_id', 'adsc_id'],
                                    name='Individual Detail Uniqueness')
        ]

    def __str__(self):
        return "{} - {}".format(self.anix_id.__str__(), self.anidc_id.__str__())

    def clean(self):
        if self.det_val > self.anidc_id.max_val or self.det_val < self.anidc_id.min_val:
            raise ValidationError({
                "det_val": ValidationError("Value {} exceeds limits. Max: {}, Min: {}".format(self.det_val,
                                                                                              self.anidc_id.max_val,
                                                                                              self.anidc_id.min_val))
            })


class IndTreatCode(BioLookup):
    # indvtc tag
    rec_dose = models.CharField(max_length=400, verbose_name=_("Recommended Dosage"))
    manufacturer = models.CharField(max_length=50, verbose_name=_("Treatment Manufacturer"))


class IndTreatment(BioModel):
    # indvt tag
    indvtc_id = models.ForeignKey('IndTreatCode', on_delete=models.DO_NOTHING,
                                  verbose_name=_("Individual Treatment Code"))
    lot_num = models.CharField(max_length=30, verbose_name=_("Lot Number"))
    dose = models.DecimalField(max_digits=7, decimal_places=3, verbose_name=_("Dose"))
    unit_id = models.ForeignKey('UnitCode', on_delete=models.DO_NOTHING, verbose_name=_("Units"))
    start_datetime = models.DateTimeField(null=True, blank=True, verbose_name=_("Start Date"))
    end_datetime = models.DateTimeField(null=True, blank=True, verbose_name=_("End Date"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{}-{}".format(self.indvtc_id.__str__(), self.lot_num)


class Instrument(BioModel):
    # inst tag
    instc_id = models.ForeignKey('InstrumentCode', on_delete=models.DO_NOTHING, verbose_name=_("Instrument Code"))
    serial_number = models.CharField(null=True, unique=True, blank=True, max_length=250,
                                     verbose_name=_("Serial Number"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{} - {}".format(self.instc_id.__str__(), self.serial_number)


class InstrumentCode(BioLookup):
    # instc tag
    pass


class InstrumentDet(BioTimeModel):
    # instd tag
    inst_id = models.ForeignKey('Instrument', on_delete=models.DO_NOTHING, verbose_name=_("Instrument"))
    instdc_id = models.ForeignKey('InstDetCode', on_delete=models.DO_NOTHING, verbose_name=_("Instrument Detail Code"))
    det_value = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Value"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['inst_id', 'instdc_id', 'start_date'], name='Instrument Detail Uniqueness')
        ]

    def __str__(self):
        return "{}-{}".format(self.instdc_id.__str__(), self.inst_id.__str__())


class InstDetCode(BioLookup):
    # instdc tag
    pass


class Location(BioModel):
    # loc tag
    evnt_id = models.ForeignKey('Event', on_delete=models.DO_NOTHING, verbose_name=_("Event"), related_name="location")
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
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{} location".format(self.locc_id.__str__())

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["evnt_id", "locc_id", "rive_id", "trib_id", "subr_id", "relc_id", "loc_lat",
                                            "loc_lon", "loc_date"], name='Location Uniqueness')
        ]


class LocCode(BioLookup):
    # Locc tag
    pass


class Organization(BioLookup):
    # orga tag
    pass


class Pairing(BioTimeModel):
    # pair tag
    indv_id = models.ForeignKey('Individual',  on_delete=models.DO_NOTHING, verbose_name=_("Dam"),
                                limit_choices_to={'ufid__isnull': False, 'indv_valid': True}, related_name="pairings")

    def __str__(self):
        return "Pair: {}-{}".format(self.indv_id.__str__(), self.start_date)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['indv_id', 'start_date'], name='Pairing Uniqueness')
        ]


class PersonnelCode(BioModel):
    # perc tag
    perc_last_name = models.CharField(max_length=32, verbose_name=_("Last Name"))
    perc_first_name = models.CharField(max_length=32, verbose_name=_("First Name"))
    perc_valid = models.BooleanField(default="False", verbose_name=_("Record still valid?"))

    def __str__(self):
        return "{} {}".format(self.perc_first_name, self.perc_last_name)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['perc_first_name', 'perc_last_name'], name='Personnel Code Uniqueness')
        ]


class PriorityCode(BioLookup):
    # prio tag
    pass


class Program(BioTimeModel):
    # prog tag
    prog_name = models.CharField(max_length=30, unique=True, verbose_name=_("Program Name"))
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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['proga_first_name', 'proga_last_name'], name='Program Authority Uniqueness')
        ]


class Protocol(BioTimeModel):
    # prot tag
    prog_id = models.ForeignKey('Program', on_delete=models.DO_NOTHING, verbose_name=_("Program"),
                                limit_choices_to={'valid': True}, related_name="protocols")
    protc_id = models.ForeignKey('ProtoCode', on_delete=models.DO_NOTHING, verbose_name=_("Protocol Code"))
    evntc_id = models.ForeignKey('EventCode', blank=True, null=True, on_delete=models.DO_NOTHING,
                                 verbose_name=_("Event Code"))
    prot_desc = models.CharField(max_length=4000, verbose_name=_("Protocol Description"))

    def __str__(self):
        return "{}, {}".format(self.protc_id.__str__(), self.prog_id.__str__())

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['prog_id', 'protc_id', 'start_date'], name='Protocol Uniqueness')
        ]


class ProtoCode(BioLookup):
    # protc tag
    pass


def protf_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/bio_diversity/protofiles/<filename>
    return 'bio_diversity/protofiles/{}'.format(filename)


class Protofile(BioModel):
    # protf tag
    prot_id = models.ForeignKey('Protocol', on_delete=models.DO_NOTHING, related_name="protf_id",
                                verbose_name=_("Protocol"), limit_choices_to={'valid': True})
    protf_pdf = models.FileField(upload_to=protf_directory_path, blank=True, null=True, verbose_name=_("Protocol File"))
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
    subr_id = models.ForeignKey('SubRiverCode', on_delete=models.DO_NOTHING, null=True, blank=True,
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

    def __str__(self):
        return "{} - {}".format(self.sampc_id.__str__(), self.samp_num)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['loc_id', 'samp_num', 'spec_id', 'sampc_id'], name='Sample Uniqueness')
        ]


class SampleCode(BioLookup):
    # sampc tag
    pass


class SampleDet(BioDet):
    samp_id = models.ForeignKey('Sample', on_delete=models.DO_NOTHING, verbose_name=_("Sample"))
    anidc_id = models.ForeignKey('AnimalDetCode', on_delete=models.DO_NOTHING, verbose_name=_("Animal Detail Code"))
    adsc_id = models.ForeignKey('AniDetSubjCode', on_delete=models.DO_NOTHING, null=True, blank=True,
                                verbose_name=_("Animal Detail Subjective Code"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['samp_id', 'anidc_id', 'adsc_id'], name='Sample Detail Uniqueness')
        ]

    def __str__(self):
        return "{} - {}".format(self.samp_id.__str__(), self.anidc_id.__str__())

    def clean(self):
        if self.det_val > self.anidc_id.max_val or self.det_val < self.anidc_id.min_val:
            raise ValidationError({
                "det_val": ValidationError("Value {} exceeds limits. Max: {}, Min: {}".format(self.det_val,
                                                                                              self.anidc_id.max_val,
                                                                                              self.anidc_id.min_val))
            })


class Sire(BioModel):
    # sire tag
    prio_id = models.ForeignKey('PriorityCode', on_delete=models.DO_NOTHING, verbose_name=_("Priority"))
    pair_id = models.ForeignKey('Pairing', on_delete=models.DO_NOTHING, verbose_name=_("Pairing"), related_name="sire",
                                limit_choices_to={'valid': True})
    indv_id = models.ForeignKey('Individual', on_delete=models.DO_NOTHING, verbose_name=_("Sire UFID"),
                                limit_choices_to={'ufid__isnull':  False, 'indv_valid': True}, related_name="sires")
    choice = models.IntegerField(verbose_name=_("Choice"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "Sire {}".format(self.indv_id.__str__())


class Spawning(BioModel):
    # spwn tag
    pair_id = models.ForeignKey('Pairing', on_delete=models.DO_NOTHING, verbose_name=_("Pairing"),
                                limit_choices_to={'valid': True})
    spwn_date = models.DateField(verbose_name=_("Date of spawning"))
    est_fecu = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Estimated Fecundity"))
    comments = models.CharField(null=True, blank=True, max_length=2000, verbose_name=_("Comments"))

    def __str__(self):
        return "{}-{}".format(self.pair_id.indv_id.__str__(), self.spwn_date)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['pair_id', 'spwn_date'], name='Spawning Uniqueness')
        ]


class SpawnDet(BioDet):
    # spwnd tag
    spwn_id = models.ForeignKey('Spawning', on_delete=models.DO_NOTHING, verbose_name=_("Spawning"))
    spwndc_id = models.ForeignKey('SpawnDetCode', on_delete=models.DO_NOTHING, verbose_name=_("Spawning Detail Code"))
    spwnsc_id = models.ForeignKey('SpawnDetSubjCode', on_delete=models.DO_NOTHING, null=True, blank=True,
                                  verbose_name=_("Spawning Detail Subjective Code"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['spwn_id', 'spwndc_id', 'spwnsc_id'], name='Spawning Detail Uniqueness')
        ]

    def __str__(self):
        return "{} - {}".format(self.spwn_id.__str__(), self.spwndc_id.__str__())

    def clean(self):
        if self.det_val > self.spwndc_id.max_val or self.det_val < self.spwndc_id.min_val:
            raise ValidationError({
                "det_val": ValidationError("Value {} exceeds limits. Max: {}, Min: {}".format(self.det_val,
                                                                                              self.spwndc_id.max_val,
                                                                                              self.spwndc_id.min_val))
            })


class SpawnDetCode(BioLookup):
    # spwndc tag
    min_val = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Minimum Value"))
    max_val = models.DecimalField(max_digits=11, decimal_places=5, verbose_name=_("Maximum Value"))
    unit_id = models.ForeignKey("UnitCode", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("Units"))
    spwn_subj_flag = models.BooleanField(verbose_name=_("Subjective?"))


class SpawnDetSubjCode(BioLookup):
    # spwnsc tag
    spwndc_id = models.ForeignKey('SpawnDetCode', on_delete=models.DO_NOTHING, verbose_name=_("Spawn Detail Code"))


class SpeciesCode(BioModel):
    # spec tag
    name = models.CharField(max_length=10, verbose_name=_("Species Name"))
    species = models.CharField(max_length=100, verbose_name=_("Species"))
    com_name = models.CharField(max_length=35, null=True, blank=True, verbose_name=_("Species Common Nme"))

    def __str__(self):
        return self.name


class StockCode(BioLookup):
    # stok tag
    pass


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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tank_id', 'contdc_id', 'start_date'], name='Tank Detail Uniqueness')
        ]

    def __str__(self):
        return "{} - {}".format(self.tank_id.__str__(), self.contdc_id.__str__())


class Team(BioModel):
    # team tag
    perc_id = models.ForeignKey("PersonnelCode", on_delete=models.DO_NOTHING, verbose_name=_("Team Member"),
                                limit_choices_to={'perc_valid': True})
    role_id = models.ForeignKey("RoleCode", on_delete=models.DO_NOTHING, verbose_name=_("Role Code"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['perc_id', 'role_id'], name='Team Uniqueness')
        ]


class Tray(BioLookup):
    # tray tag
    pass


class TrayDet(BioContainerDet):
    # trayd tag
    tray_id = models.ForeignKey('Tray', on_delete=models.DO_NOTHING, verbose_name=_("Tray"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tray_id', 'contdc_id', 'start_date'], name='Tray Detail  Uniqueness')
        ]

    def __str__(self):
        return "{} - {}".format(self.tray_id.__str__(), self.contdc_id.__str__())


class Tributary(BioLookup):
    # trib tag
    rive_id = models.ForeignKey('RiverCode', on_delete=models.DO_NOTHING, verbose_name=_("River"))


class Trough(BioLookup):
    # trof tag
    pass


class TroughDet(BioContainerDet):
    # trofd tag
    trof_id = models.ForeignKey('Trough', on_delete=models.DO_NOTHING, verbose_name=_("Trough"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['trof_id', 'contdc_id', 'start_date'], name='Trough Detail Uniqueness')
        ]

    def __str__(self):
        return "{} - {}".format(self.trof_id.__str__(), self.contdc_id.__str__())


class UnitCode(BioLookup):
    # unit tag
    pass
