from django.db import models
# from django.db.models import AutoField
from django.utils.translation import gettext_lazy as _

from shared_models import models as shared_models
from projects import models as project_models


# ----------------------------------------------------------------------------------------------------
#
class Lookup(models.Model):
    name_en = models.CharField(max_length=255, unique=True)
    name_fr = models.CharField(max_length=255, unique=True)

    description_en = models.TextField(null=True, blank=True)
    description_fr = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}/{}".format(self.name_en, self.name_fr)

    class Meta:
        abstract = True


# ----------------------------------------------------------------------------------------------------
# Create models for contacts
#
class CohHonorific(shared_models.Lookup):
    pass


class CotType(shared_models.Lookup):
    pass


class LanLanguage(shared_models.Lookup):
    pass


class NotNotificationPreference(shared_models.Lookup):
    pass


class RolRole(shared_models.Lookup):
    pass


class SecSector(shared_models.Lookup):
    pass


class ConContact(models.Model):
    honorific = models.ForeignKey(CohHonorific, on_delete=models.DO_NOTHING, verbose_name=_("Honorific"))
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    affiliation = models.CharField(max_length=100, verbose_name=_("Affiliation"))
    job_title = models.CharField(max_length=100, verbose_name=_("Job Title"))
    language = models.ForeignKey(LanLanguage, on_delete=models.DO_NOTHING, verbose_name=_("Language"))
    contact_type = models.ForeignKey(CotType, on_delete=models.DO_NOTHING, verbose_name=_("Contact Type"))
    notification_preference = models.ForeignKey(NotNotificationPreference, models.DO_NOTHING,
                                                verbose_name=_("Notification Preference"))
    phone = models.CharField(max_length=12, verbose_name=_("Phone"))
    email = models.CharField(max_length=255, verbose_name=_("E-mail"))
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, blank=True, null=True,
                               verbose_name=_("Region"))
    sector = models.ForeignKey(SecSector, on_delete=models.DO_NOTHING, verbose_name=_("Sector"))
    role = models.ForeignKey(RolRole, on_delete=models.DO_NOTHING,
                             help_text=_("Indicates permissions i.e. regional coordinator, regional science adviser, "
                                         "regional admin, director, etc."),
                             verbose_name=_("Role"))
    expertise = models.CharField(max_length=100, verbose_name=_("Expertise"))
    cc_grad = models.BooleanField(verbose_name=_("Chair Course Graduate"))
    notes = models.TextField(verbose_name=_("Notes"))

    def __str__(self):
        return "{}, {}".format(self.last_name, self.first_name)


# ----------------------------------------------------------------------------------------------------
# Create models for meetings
#
class FilFile(models.Model):
    file = models.BooleanField()

    def __str__(self):
        return "{}".format(self.file)


class MftMeetingFileType(models.Model):
    name = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)


class SttStatus(shared_models.Lookup):
    pass


class ScpScope(shared_models.Lookup):
    pass


class AptAdvisoryProcessType(shared_models.Lookup):
    pass


class LocLocation(shared_models.Lookup):
    pass


class MeqQuarter(shared_models.Lookup):
    pass


class MetMeeting(models.Model):
    quarter = models.ForeignKey(MeqQuarter, on_delete=models.DO_NOTHING)
    start_date = models.DateField(null=True, blank=True, verbose_name=_("Start Date"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("End_Date"))
    title_en = models.CharField(max_length=255, verbose_name=_("Title (English)"))
    title_fr = models.CharField(max_length=255, verbose_name=_("Title (French)"))
    scope = models.ForeignKey(ScpScope, on_delete=models.DO_NOTHING, verbose_name=_("Scope"))
    status = models.ForeignKey(SttStatus, on_delete=models.DO_NOTHING, verbose_name=_("Status"))
    chair_comments = models.TextField(null=True, blank=True, verbose_name=_("Chair Comments"))
    status_notes = models.TextField(null=True, blank=True, verbose_name=_("Status Notes"))
    location = models.ForeignKey(LocLocation, on_delete=models.DO_NOTHING, verbose_name=_("Location"))
    lead_region = models.ForeignKey(shared_models.Region, blank=True, on_delete=models.DO_NOTHING,
                                    verbose_name=_("Lead Region"))
    other_region = models.ManyToManyField(shared_models.Region, blank=True, related_name="other_regions",
                                          verbose_name=_("Other Region"))
    process_type = models.ForeignKey(AptAdvisoryProcessType, on_delete=models.DO_NOTHING,
                                     verbose_name=_("Process Type"))
    program_contact = models.ManyToManyField(ConContact, blank=True, related_name="program_contacts",
                                             verbose_name=_("Program Contact"))
    csas_contact = models.ManyToManyField(ConContact, blank=True, related_name="csas_contacts",
                                          verbose_name=_("CSAS Contact"))

    def __str__(self):
        return "{}/{}".format(self.title_en, self.title_fr)


class MecMeetingContact(models.Model):
    meeting = models.ForeignKey(MetMeeting, on_delete=models.DO_NOTHING)
    contact = models.ForeignKey(ConContact, on_delete=models.DO_NOTHING)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.meeting)


class OmCost(models.Model):
    amount = models.DecimalField(decimal_places=10, max_digits=20)
    funding_source = models.ForeignKey(project_models.FundingSource, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(project_models.OMCategory, on_delete=models.DO_NOTHING)

    description = models.TextField()

    def __str__(self):
        return "{}".format(self.pk)


class PsePublicationSeries(models.Model):
    pass

    def __str__(self):
        return "{}".format(self.pk)


class MefMeetingFile(models.Model):
    meeting = models.ForeignKey(MetMeeting, on_delete=models.DO_NOTHING)
    file_en = models.ForeignKey(FilFile, on_delete=models.DO_NOTHING, related_name="file_en")
    file_fr = models.ForeignKey(FilFile, on_delete=models.DO_NOTHING, related_name="file_fr")
    document_type = models.ForeignKey(MftMeetingFileType, on_delete=models.DO_NOTHING)
    date_submitted = models.DateField(blank=True, null=True, verbose_name=_("Date Submitted"))
    date_posted = models.DateField(blank=True, null=True, verbose_name=_("Date Postted"))

    def __str__(self):
        return "{}".format(self.meeting)


class MerOtherRegion(models.Model):
    meeting = models.ForeignKey(MetMeeting, on_delete=models.DO_NOTHING)
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}".format(self.meeting)


class MomMeetingOmCost(models.Model):
    met_id = models.ForeignKey(MetMeeting, on_delete=models.DO_NOTHING)
    om_id = models.ForeignKey(OmCost, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}".format(self.pk)


# ----------------------------------------------------------------------------------------------------
# Create models for publications
#
class PseSeries(shared_models.Lookup):
    name = models.CharField(max_length=50)


class KeyKeywords(shared_models.Lookup):
    name = models.CharField(max_length=100)


class PubPublication(models.Model):
    series = models.ForeignKey(PsePublicationSeries, null=True, blank=True, on_delete=models.DO_NOTHING,
                               verbose_name=_("Series"))
    scope = models.ForeignKey(ScpScope, null=True, blank=True, on_delete=models.DO_NOTHING, verbose_name=_("Scope"))
    lead_region = models.ForeignKey(shared_models.Region, null=True, blank=True, on_delete=models.DO_NOTHING,
                                    verbose_name=_("Lead Region"))
    lead_author = models.ForeignKey(ConContact, null=True, blank=True, on_delete=models.DO_NOTHING,
                                    verbose_name=_("Lead Author"))
    pub_year = models.IntegerField(null=True, blank=True, verbose_name=_("Publication Year"))
    pub_num = models.CharField(max_length=25, verbose_name=_("Publication Number"))
    pages = models.IntegerField(null=True, blank=True, verbose_name=_("Pages"))
    citation = models.TextField(null=True, blank=True, verbose_name=_("Citation"))
    location = models.ForeignKey(LocLocation, null=True, blank=True, on_delete=models.DO_NOTHING,
                                 verbose_name=_("Documentation Location"))

    def __str__(self):
        return "{}".format(self.lead_author)


class MepExpectedPublication(models.Model):
    meeting = models.ForeignKey(MetMeeting, on_delete=models.DO_NOTHING)
    publication = models.ForeignKey(PubPublication, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}".format(self.publication)


class PurOtherRegion(models.Model):
    pub_id = models.ForeignKey(PubPublication, on_delete=models.DO_NOTHING)
    reg_id = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, blank=True, null=True)


class PuaOtherAuthor(models.Model):
    pub_id = models.ForeignKey(PubPublication, on_delete=models.DO_NOTHING)
    con_id = models.ForeignKey(ConContact, on_delete=models.DO_NOTHING)


class PukPublicationKeyword(models.Model):
    pub_id = models.ForeignKey(PubPublication, on_delete=models.DO_NOTHING)
    key_id = models.ForeignKey(KeyKeywords, on_delete=models.DO_NOTHING)


class PtiPublicationTitle(models.Model):
    pst_title = models.AutoField(primary_key=True)
    publication = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=100)
    language = models.ForeignKey(LanLanguage, on_delete=models.DO_NOTHING, null=True, blank=True)


# ----------------------------------------------------------------------------------------------------
# Create models for requests
#
class RepPriority(shared_models.Lookup):
    pass


class RetTiming(shared_models.Lookup):
    pass


class RedDecision(models.Model):
    name = models.CharField(max_length=100)


class ReqRequest(models.Model):
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
    # decision_explanation = models.TextField(max_length=100, verbose_name=_("Decision Explanation"))
    adviser_submission = models.DateField(null=True, blank=True, verbose_name=_("Client Adviser Submission Date"))
    rd_submission = models.DateField(null=True, blank=True, verbose_name=_("Client RD Submission Date"))
    decision_date = models.DateField(null=True, blank=True, verbose_name=_("Decision Date"))

    def __str__(self):
        return "{}".format(self.title)


# End of models.py
# ----------------------------------------------------------------------------------------------------
# 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
#
# class OthOther(models.Model):
#     oth_id = models.AutoField(primary_key=True)
#     oth_num = models.CharField(max_length=25)
#
#     def __str__(self):
#         return "{}".format(self.oth_num)
