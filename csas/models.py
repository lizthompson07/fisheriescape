from django.db import models
from django.utils.translation import gettext_lazy as _

from shared_models import models as shared_models
from projects import models as project_models


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
    lan_id = models.AutoField(primary_key=True)    # should this be AutoField or fixed? <- Good question, I don't know - Patrick


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
    contact_type = models.ForeignKey(CotType, on_delete=models.DO_NOTHING)
    notification_preference = models.ForeignKey(NotNotificationPreference, models.DO_NOTHING)
    phone = models.CharField(max_length=12)
    email = models.CharField(max_length=255)
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, blank=True, null=True)
    section = models.ForeignKey(SecSector, on_delete=models.DO_NOTHING)
    role = models.ForeignKey(RolRole, on_delete=models.DO_NOTHING)
    expertise = models.CharField(max_length=100)
    cc_grad = models.BooleanField()
    notes = models.TextField()

    def __str__(self):
        return "{}, {}".format(self.last_name, self.first_name)


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


class LocLocation(Lookup):
    loc_id = models.AutoField(primary_key=True)


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

    other_region = models.ManyToManyField(shared_models.Region, related_name="other_regions")

    process_type = models.ForeignKey(AptAdvisoryProcessType, on_delete=models.DO_NOTHING)

    program_contact = models.ManyToManyField(ConContact, related_name="program_contacts")
    csas_contact = models.ManyToManyField(ConContact, related_name="csas_contacts")

    def __str__(self):
        return "{}/{}".format(self.title_en, self.title_fr)


class MecMeetingContact(models.Model):
    mec_id = models.CharField(max_length=45)
    meeting = models.ForeignKey(MetMeeting, on_delete=models.DO_NOTHING)
    contact = models.ForeignKey(ConContact, on_delete=models.DO_NOTHING)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.meeting)


# Yongcun: Delete this comment when you've read it.
# 1) I removed the FundingSource and OmCategory classes.
# 2) I imported the projects application model as project_models
# 3) I updated OmCost so that it's linking to the project_modes.FundingSource and OmCategory
class OmCost(models.Model):
    om_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(decimal_places=10, max_digits=20)
    funding_source = models.ForeignKey(project_models.FundingSource, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(project_models.OMCategory, on_delete=models.DO_NOTHING)

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


# Is it wrong that file_en, file_fr point to the same foreign key?
#
# yes, and no. They can have the same ForeignKey, but you have to specify a 'related_name' (I've added)
# so python won't complain - Patrick
#
class MefMeetingFile(models.Model):
    mef_id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(MetMeeting, on_delete=models.DO_NOTHING)
    file_en = models.ForeignKey(FilFile, on_delete=models.DO_NOTHING, related_name="file_en")
    file_fr = models.ForeignKey(FilFile, on_delete=models.DO_NOTHING, related_name="file_fr")
    document_type = models.ForeignKey(MftMeetingFileType, on_delete=models.DO_NOTHING)
    date_submitted = models.DateField(blank=True, null=True, verbose_name=_("Date Submitted"))
    date_posted = models.DateField(blank=True, null=True, verbose_name=_("Date Postted"))

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
class RepPriority(Lookup):
    rep_id = models.AutoField(primary_key=True)


class RetTiming(Lookup):
    ret_id = models.AutoField(primary_key=True)


class RedDecision(models.Model):
    red_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)


class ReqRequest(models.Model):
    req_id = models.AutoField(primary_key=True, verbose_name=_("Request ID"))
    assigned_req_id = models.CharField(max_length=45, verbose_name=_("Assigned Request Number"))
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    in_year_request = models.BooleanField(verbose_name=_("In-Year Request"))
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, blank=True, null=True)
    client_sector = models.ForeignKey(SecSector, on_delete=models.DO_NOTHING, verbose_name=_("Client Sector"))
    client_name = models.CharField(max_length=100, verbose_name=_("Client Name"))
    client_title = models.CharField(max_length=100, verbose_name=_("Client Title"))
    client_email = models.CharField(max_length=255, verbose_name=_("Client E-mail"))
    issue = models.TextField(verbose_name=_("Issue"),
                             help_text=_("Issue requiring science information and/or advice. Posted as a question "
                                         "to be answered by Science."))
    priority = models.ForeignKey(RepPriority, on_delete=models.DO_NOTHING, verbose_name=_("Priority"))
    rationale = models.TextField(verbose_name=_("Rationale for Request"),
                                 help_text=_("Rationale or context for the request: What will the information/advice "
                                             "be used for? Who will be the end user(s)? Will it impact other DFO "
                                             "programs or regions?"))
    proposed_timing = models.ForeignKey(RetTiming, on_delete=models.DO_NOTHING, verbose_name=_("Proposed Timing"),
                                        help_text=_("Latest possible date to receive Science Advice."))
    rationale_for_timing = models.TextField(verbose_name=_("Rationale for Timing"),
                                            help_text=_("Explain rationale for proposed timing."))
    funding = models.BooleanField(help_text=_("Do you have funds to cover extra costs associated with this request?"))
    funding_notes = models.TextField(max_length=100, verbose_name=_("Funding Notes"))
    science_discussion = models.BooleanField(verbose_name=_("Science Discussion"),
                                             help_text=_("Have you talked to Science about this request?"))
    science_discussion_notes = models.CharField(max_length=100, verbose_name=_("Science Discussion Notes"),
                                                help_text=_("If you have talked to Science about this request, "
                                                            "to whom have you talked?"))
    # decision = models.ForeignKey(RedDecision, on_delete=models.DO_NOTHING, blank=True, null=True)
    # decision = models.ForeignKey(CotType, on_delete=models.DO_NOTHING)    # CotType is borrowed from Contacts
    # decision_explanation = models.TextField()
    adviser_submission = models.DateField(null=True, blank=True, verbose_name=_("Client Adviser Submission Date"))
    rd_submission = models.DateField(null=True, blank=True, verbose_name=_("Client RD Submission Date"))
    decision_date = models.DateField(null=True, blank=True, verbose_name=_("Decision Date"))

    def __str__(self):
        return "{}".format(self.title)


# ---------------------------------------------------------------------------------------
# Create models for publications
class OthOther(models.Model):
    oth_id = models.AutoField(primary_key=True)
    oth_num = models.CharField(max_length=25)

    def __str__(self):
        return "{}".format(self.oth_num)

