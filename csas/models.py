from django.db import models
from django.utils.translation import gettext_lazy as _

from shared_models import models as shared_models

# ---------------------------------------------------------------------------------------
# Create models for contacts
class CohHonorific(models.Model):
    coh_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, verbose_name="Honorific")

    def __str__(self):
        return "{}".format(self.name)


class CotType(models.Model):
    cot_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)


class LanLanguage(models.Model):
    lan_id = models.AutoField(primary_key=True)    # should this be AutoField or fixed?
    name = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)


class NotNotificationPreference(models.Model):
    not_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)


class RolRole(models.Model):
    role_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)


class SecSector(models.Model):
    sec_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)


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


class SttStatus(models.Model):
    stt_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return "{}".format(self.name)


class ScpScope(models.Model):
    scp_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return "{}".format(self.name)


class AptAdvisoryProcessType(models.Model):
    apt_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.name)


class MctContactType(models.Model):
    mct_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.name)


class LocLocation(models.Model):
    mct_id = models.AutoField(primary_key=True)
    # name = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.mct_id)

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


class AdvisoryProcessType(models.Model):
    apt_id = models.AutoField(primary_key=True)
    # name = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.apt_id)


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


class MetMeeting(models.Model):
    met_id = models.AutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    title_en = models.CharField(max_length=255)
    title_fr = models.CharField(max_length=255)
    scope = models.ForeignKey(ScpScope, on_delete=models.DO_NOTHING)
    status = models.ForeignKey(SttStatus, on_delete=models.DO_NOTHING)
    chair_comments = models.TextField()
    status_notes = models.TextField()
    location = models.ForeignKey(LocLocation, on_delete=models.DO_NOTHING)
    lead = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING)
    process_type = models.ForeignKey(AdvisoryProcessType, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}".format(self.title_en)


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

