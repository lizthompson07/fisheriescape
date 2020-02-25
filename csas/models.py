from django.db import models
from django.utils.translation import gettext_lazy as _

from shared_models import models as shared_models

# ---------------------------------------------------------------------------------------
class Lookup(models.Model):
    name_en = models.CharField(max_length=255, unique=True)
    name_fr = models.CharField(max_length=255, unique=True)

    description_en = models.TextField(null=True, blank=True)
    description_fr = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}/{}".format(self.name_en, self.name_fr)

    class Meta:
        abstract = True


class CohHonorific(Lookup):
    coh_id = models.AutoField(primary_key=True)


class CotType(Lookup):
    cot_id = models.AutoField(primary_key=True)


class LanLanguage(Lookup):
    lan_id = models.AutoField(primary_key=True)    # should this be AutoField or fixed?


class NotNotificationPreference(Lookup):
    not_id = models.AutoField(primary_key=True)


class RolRole(Lookup):
    role_id = models.AutoField(primary_key=True)


class SecSector(Lookup):
    sec_id = models.AutoField(primary_key=True)


class ConContact(models.Model):
    con_id = models.AutoField(primary_key=True)
    honorific = models.ForeignKey(CohHonorific, on_delete=models.DO_NOTHING)
    first_name = models.CharField(max_length=100, help_text=_("Some help here"))
    last_name = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    language = models.ForeignKey(LanLanguage, on_delete=models.DO_NOTHING)
    contact_type = models.ForeignKey(CotType, on_delete=models.DO_NOTHING)    # should use IntegerField or ForeignKey
    notification_preference = models.ForeignKey(NotNotificationPreference, models.DO_NOTHING)    # should use IntegerField or ForeignKey
    phone = models.CharField(max_length=12)
    email = models.CharField(max_length=255)
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING)
    section = models.ForeignKey(SecSector, on_delete=models.DO_NOTHING)    # should use IntegerField or ForeignKey
    role = models.ForeignKey(RolRole, on_delete=models.DO_NOTHING)    # should use IntegerField or ForeignKey
    expertise = models.CharField(max_length=100)
    cc_grad = models.BooleanField()    # what is TINYINT
    notes = models.TextField()   # what is MEDIUMTEXT

    def __str__(self):
        return "{}".format(self.last_name)


# ---------------------------------------------------------------------------------------
# Create models for meetings
class FilFile(models.Model):
    fil_id = models.AutoField(primary_key=True)
    file = models.BooleanField()

    def __str__(self):
        return "{}".format(self.file)


class MftMeetingFileType(models.Model):
    mft_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)


class SttStatus(Lookup):
    stt_id = models.AutoField(primary_key=True)


class ScpScope(Lookup):
    scp_id = models.AutoField(primary_key=True)


class AptAdvisoryProcessType(Lookup):
    apt_id = models.AutoField(primary_key=True)


class MctContactType(Lookup):
    mct_id = models.AutoField(primary_key=True)


class LocLocation(Lookup):
    mct_id = models.AutoField(primary_key=True)


# following several classes should be shared_models like Region, but we don't have them, so we define them here now,
# they will be removed late
class FundingSource(models.Model):
    fs_id = models.AutoField(primary_key=True)
    # name = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.fs_id)


class OmCategory(models.Model):
    omc_id = models.AutoField(primary_key=True)
    # name = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.omc_id)


class OmCost(models.Model):
    om_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(decimal_places=10, max_digits=20)
    funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(OmCategory, on_delete=models.DO_NOTHING)
    description = models.TextField()

    def __str__(self):
        return "{}".format(self.om_id)


class PsePublicationSeries(models.Model):
    pse_id = models.AutoField(primary_key=True)
    # name = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.pse_id)


class PubPublicationDetails(models.Model):
    pub_id = models.AutoField(primary_key=True)
    series = models.ForeignKey(PsePublicationSeries, on_delete=models.DO_NOTHING)
    scope = models.ForeignKey(ScpScope, on_delete=models.DO_NOTHING)
    lead_region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING)
    lead_author = models.ForeignKey(ConContact, on_delete=models.DO_NOTHING)
    pub_year = models.IntegerField()
    pub_number = models.CharField(max_length=25)
    pages = models.IntegerField()
    citation = models.TextField()
    location = models.ForeignKey(LocLocation, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}".format(self.lead_author)


class MeqQuarter(Lookup):
    meq_id = models.AutoField(primary_key=True)


class MetMeeting(models.Model):
    met_id = models.AutoField(primary_key=True)
    quarter = models.ForeignKey(MeqQuarter, on_delete=models.DO_NOTHING)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    title_en = models.CharField(max_length=255)
    title_fr = models.CharField(max_length=255)
    scope = models.ForeignKey(ScpScope, on_delete=models.DO_NOTHING)
    status = models.ForeignKey(SttStatus, on_delete=models.DO_NOTHING)
    chair_comments = models.TextField(null=True, blank=True)
    status_notes = models.TextField(null=True, blank=True)
    location = models.ForeignKey(LocLocation, on_delete=models.DO_NOTHING)
    lead_region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING)
    process_type = models.ForeignKey(AptAdvisoryProcessType, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}/{}".format(self.title_en, self.title_fr)


# Is it wrong that file_en, file_fr point to the same foreign key?
class MefMeetingFile(models.Model):
    mef_id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(MetMeeting, on_delete=models.DO_NOTHING)
    file_en = models.IntegerField()
    file_fr = models.ForeignKey(FilFile, on_delete=models.DO_NOTHING)
    document_type = models.ForeignKey(MftMeetingFileType, on_delete=models.DO_NOTHING)
    date_submitted = models.DateField(blank=True, null=True, verbose_name=_("Date Submitted"))
    date_posted = models.DateField(blank=True, null=True, verbose_name=_("Date Postted"))

    def __str__(self):
        return "{}".format(self.meeting)


class MecMeetingContact(models.Model):
    mec_id = models.CharField(max_length=45)
    meeting = models.ForeignKey(MetMeeting, on_delete=models.DO_NOTHING)
    contact = models.ForeignKey(ConContact, on_delete=models.DO_NOTHING)
    contact_type = models.ForeignKey(MctContactType, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}".format(self.meeting)


class MerOtherRegion(models.Model):
    mer_id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(MetMeeting, on_delete=models.DO_NOTHING)
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}".format(self.meeting)


class MomMeetingOmCost(models.Model):
    mom_id = models.AutoField(primary_key=True)
    met_id = models.ForeignKey(MetMeeting, on_delete=models.DO_NOTHING)
    om_id = models.ForeignKey(OmCost, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}".format(self.mom_id)


class MepExpectedPublication(models.Model):
    mep_id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(MetMeeting, on_delete=models.DO_NOTHING)
    publication = models.ForeignKey(PubPublicationDetails, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}".format(self.publication)


# ---------------------------------------------------------------------------------------
# Create models for publications
class PubPublication(models.Model):
    put_id = models.AutoField(primary_key=True)
    pub_num = models.CharField(max_length=25)

    def __str__(self):
        return "{}".format(self.pub_num)


# ---------------------------------------------------------------------------------------
# Create models for requests
class ReqRequest(models.Model):
    req_id = models.AutoField(primary_key=True)
    title_en = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.title_en)


# ---------------------------------------------------------------------------------------
# Create models for publications
class OthOther(models.Model):
    oth_id = models.AutoField(primary_key=True)
    oth_num = models.CharField(max_length=25)

    def __str__(self):
        return "{}".format(self.oth_num)

