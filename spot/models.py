import datetime

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models
from masterlist import models as ml_models


class Status(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name (English)"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("name (French)"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = [_('name'), ]


class Program(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name (English)"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("name (French)"))
    abbrev_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("abbreviation (French)"))
    abbrev_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("abbreviation (French)"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = [_('name'), ]


class Project(models.Model):
    # choices for risk_assessment_score
    LOW = 1
    MED = 2
    HIGH = 3
    RISK_ASSESSMENT_SCORE_CHOICES = (
        (LOW, "low"),
        (MED, "medium"),
        (HIGH, "high"),
    )

    finance_id = models.CharField(max_length=50, blank=True, null=True)
    tracking_system_id = models.CharField(max_length=50, blank=True, null=True)
    organization = models.ForeignKey(ml_models.Organization, on_delete=models.DO_NOTHING, related_name="projects")
    program = models.ForeignKey(Program, on_delete=models.DO_NOTHING, related_name="projects")
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="projects")
    regions = models.ManyToManyField(shared_models.Region)
    start_year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, related_name="gc_projects")

    title = models.TextField()
    title_abbrev = models.CharField(max_length=150, blank=True, null=True)
    project_length = models.IntegerField(blank=True, null=True)
    risk_assessment_score = models.IntegerField(blank=True, null=True, choices=RISK_ASSESSMENT_SCORE_CHOICES)
    date_completed = models.DateTimeField(blank=True, null=True)

    requested_funding_y1 = models.FloatField(blank=True, null=True, verbose_name=_("requested funding (year 1)"))
    requested_funding_y2 = models.FloatField(blank=True, null=True, verbose_name=_("requested funding (year 2)"))
    requested_funding_y3 = models.FloatField(blank=True, null=True, verbose_name=_("requested funding (year 3)"))

    regional_score = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)

    application_submission_date = models.DateTimeField(blank=True, null=True)
    language = models.ForeignKey(shared_models.Language, on_delete=models.DO_NOTHING, related_name="projects", verbose_name=_("project language"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("project notes"))
    recommended_funding_y1 = models.FloatField(blank=True, null=True, verbose_name=_("recommended funding (year 1)"))
    recommended_funding_y2 = models.FloatField(blank=True, null=True, verbose_name=_("recommended funding (year 2)"))
    recommended_funding_y3 = models.FloatField(blank=True, null=True, verbose_name=_("recommended funding (year 3)"))
    recommended_overprogramming = models.FloatField(blank=True, null=True)
    negotiations_workplan_completion_date = models.DateTimeField(blank=True, null=True)
    negotiations_financials_completion_date = models.DateTimeField(blank=True, null=True)
    regrets_or_op_letter_sent_date = models.DateTimeField(blank=True, null=True)

    @property
    def total_requested_funding(self):
        return sum([
            self.requested_funding_y1,
            self.requested_funding_y2,
            self.requested_funding_y3,
        ])

    @property
    def total_recommended_funding(self):
        return sum([
            self.recommended_funding_y1,
            self.recommended_funding_y2,
            self.recommended_funding_y3,
        ])

    @property
    def negotiation_completion_date(self):
        """ this will be the max of negotiations_workplan_completion_date and negotiations_financials_completion_date"""
        return max(self.negotiations_workplan_completion_date, self.negotiations_financials_completion_date )


class InitiationType(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name (English)"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("name (French)"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = [_('name'), ]


# def draft_ca_file_directory_path(instance, filename):
#     # file will be uploaded to MEDIA_ROOT/entry_<id>/<filename>
#     return 'spot/{0}/{0}_draft_contribution_agreement.pdf'.format(instance.id)
#
#
# class ProjectYear(models.Model):
#
#     project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name="projects", verbose_name=_("project language"))
#     fiscal_year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, related_name="projects")
#     expenditure_initiation_date = models.DateTimeField(blank=True, null=True, default=datetime.datetime(timezone.now().year, 4, 1))
#     paye_number = models.CharField(max_length=50, blank=True, null=True)
#     annual_funding = models.FloatField(blank=True, null=True)
#     initiation_date = models.DateTimeField(blank=True, null=True)
#     initiation_type = models.ForeignKey(InitiationType, on_delete=models.DO_NOTHING, related_name="projects")
#     initiation_acknowledgement_sent = models.DateTimeField(blank=True, null=True)
#     eoi_coordinator_notified = models.DateTimeField(blank=True, null=True)
#     eoi_feedback_sent = models.DateTimeField(blank=True, null=True)
#     negotiation_letter_sent = models.DateTimeField(blank=True, null=True)
#     schedule_5_complete = models.DateTimeField(blank=True, null=True)
#     draft_ca_ready = models.DateTimeField(blank=True, null=True)
#     draft_ca_sent_to_proponent = models.DateTimeField(blank=True, null=True)
#     draft_ca_proponent_approved = models.DateTimeField(blank=True, null=True)
#
#     # CA Checklist stuff
#     ca_checklist_complete = models.DateTimeField(blank=True, null=True) # this field might be redundant
#     draft_ca_sent_to_manager = models.DateTimeField(blank=True, null=True)
#     draft_ca_manager_approved = models.DateTimeField(blank=True, null=True)
#     draft_ca = models.FileField
#
#
#     gcafready = models.TextField(db_column='GCAFReady', blank=True, null=True) This field type is a guess.
#     raready = models.TextField(db_column='RAReady', blank=True, null=True) This field type is a guess.
#     camgrsigned = models.DateTimeField(db_column='CAMgrSigned', blank=True, null=True)
#     caprfmgrsent = models.DateTimeField(db_column='CAPRFMgrSent', blank=True, null=True)
#     caprfclientsent = models.DateTimeField(db_column='CAPRFClientSent', blank=True, null=True)
#     caclientsigned = models.TextField(db_column='CAClientSigned', blank=True, null=True) This field type is a guess.
#     catemplate2drive = models.TextField(db_column='CATemplate2Drive', blank=True, null=True) This field type is a guess.
#     ca2drive = models.DateTimeField(db_column='CA2Drive', blank=True, null=True)
#     completedcaclientsent = models.DateTimeField(db_column='CompletedCAClientSent', blank=True, null=True)
#     gcaffmaapproved = models.DateTimeField(db_column='GCAFFMAApproved', blank=True, null=True)
#     gcaffmasent = models.DateTimeField(db_column='GCAFFMASent', blank=True, null=True)
#     gcafmgrsigned = models.TextField(db_column='GCAFMgrSigned', blank=True, null=True) This field type is a guess.
#     gcaframgrsent = models.DateTimeField(db_column='GCAFRAMgrSent', blank=True, null=True)
#     gcaf2drive = models.TextField(db_column='GCAF2Drive', blank=True, null=True) This field type is a guess.
#     gcafupdated = models.TextField(db_column='GCAFUpdated', blank=True, null=True) This field type is a guess.
#     lon2drive = models.TextField(db_column='LoN2Drive', blank=True, null=True) This field type is a guess.
#     olaready = models.TextField(db_column='OLAReady', blank=True, null=True) This field type is a guess.
#     prfmgrsigned = models.TextField(db_column='PRFMgrSigned', blank=True, null=True) This field type is a guess.
#     prfready = models.TextField(db_column='PRFReady', blank=True, null=True) This field type is a guess.
#     prfapesent = models.DateTimeField(db_column='PRFAPESent', blank=True, null=True)
#     prfclientsigned = models.TextField(db_column='PRFClientSigned', blank=True, null=True) This field type is a guess.
#     prf2drive = models.TextField(db_column='PRF2Drive', blank=True, null=True) This field type is a guess.
#     ramgrsigned = models.TextField(db_column='RAMgrSigned', blank=True, null=True) This field type is a guess.
#     ra2drive = models.TextField(db_column='RA2Drive', blank=True, null=True) This field type is a guess.
#     amendmentsent = models.DateTimeField(db_column='AmendmentSent', blank=True, null=True)
#     annualcashflowapproved = models.TextField(db_column='AnnualCashflowApproved', blank=True, null=True) This field type is a guess.
#     annualcashflowready = models.DateTimeField(db_column='AnnualCashflowReady', blank=True, null=True)
#     workplanreviewcomplete = models.DateTimeField(db_column='WorkplanReviewComplete', blank=True, null=True)
#     financialreviewcomplete = models.DateTimeField(db_column='FinancialReviewComplete', blank=True, null=True)
#     myupdatercvd = models.DateTimeField(db_column='MYUpdateRcvd', blank=True, null=True)
#     myupdateadminnotified = models.DateTimeField(db_column='MYUpdateAdminNotified', blank=True, null=True)
#     pamyupdatechanges2financialsid = models.IntegerField(db_column='PAMYUpdateChanges2FinancialsID', blank=True, null=True)
#     pamyupdatechanges2workplanid = models.IntegerField(db_column='PAMYUpdateChanges2WorkplanID', blank=True, null=True)
#     myupdatereviewcomplete = models.DateTimeField(db_column='MYUpdateReviewComplete', blank=True, null=True)
#     lonsavedaspdf = models.TextField(db_column='LoNSavedAsPDF', blank=True, null=True) This field type is a guess.
#     casavedaspdf = models.TextField(db_column='CASavedAsPDF', blank=True, null=True) This field type is a guess.
#     gcafsavedaspdf = models.TextField(db_column='GCAFSavedAsPDF', blank=True, null=True) This field type is a guess.
#     notifyadmin = models.DateTimeField(db_column='NotifyAdmin', blank=True, null=True)
#     appendixeaspdf = models.TextField(db_column='AppendixEAsPDF', blank=True, null=True) This field type is a guess.
#     rasavedaspdf = models.TextField(db_column='RASavedAsPDF', blank=True, null=True) This field type is a guess.
#     auditrcvd = models.DateTimeField(db_column='AuditRcvd', blank=True, null=True)
#     coordinatornotes = models.TextField(db_column='CoordinatorNotes', blank=True, null=True)
#     forecastingnotes = models.TextField(db_column='ForecastingNotes', blank=True, null=True)
#     forecastingflagged = models.TextField(db_column='ForecastingFlagged', blank=True, null=True) This field type is a guess.
#     qr3emailsent = models.DateTimeField(db_column='QR3EmailSent', blank=True, null=True)
#     qr3reminder = models.DateTimeField(db_column='QR3Reminder', blank=True, null=True)
#     qr3forecastcomplete = models.DateTimeField(db_column='QR3ForecastComplete', blank=True, null=True)
#     qr3forecastresponseid = models.IntegerField(db_column='QR3ForecastResponseID', blank=True, null=True)
#     qr3forecastresponsedate = models.DateTimeField(db_column='QR3ForecastResponseDate', blank=True, null=True)
#     qr3interimreportdate = models.DateTimeField(db_column='QR3InterimReportDate', blank=True, null=True)
#     qr3interimreportreviewed = models.DateTimeField(db_column='QR3InterimReportReviewed', blank=True, null=True)
#     qr3interimreportapproved = models.DateTimeField(db_column='QR3InterimReportApproved', blank=True, null=True)
#     qr3interimreport2drive = models.TextField(db_column='QR3InterimReport2Drive', blank=True, null=True) This field type is a guess.
#     qr3payment = models.TextField(db_column='QR3Payment', blank=True, null=True) This field type is a guess.
#     qr3paymentclaim = models.IntegerField(db_column='QR3PaymentClaim', blank=True, null=True)
#     qr4emailsent = models.DateTimeField(db_column='QR4EmailSent', blank=True, null=True)
#     qr4reminder = models.DateTimeField(db_column='QR4Reminder', blank=True, null=True)
#     qr4forecastcomplete = models.DateTimeField(db_column='QR4ForecastComplete', blank=True, null=True)
#     qr4forecastresponseid = models.IntegerField(db_column='QR4ForecastResponseID', blank=True, null=True)
#     qr4forecastresponsedate = models.DateTimeField(db_column='QR4ForecastResponseDate', blank=True, null=True)
#     qr4payment = models.TextField(db_column='QR4Payment', blank=True, null=True) This field type is a guess.
#     qr4paymentclaim = models.IntegerField(db_column='QR4PaymentClaim', blank=True, null=True)
#     commentsfromboard = models.TextField(db_column='CommentsFromBoard', blank=True, null=True)
#     commentsworkplan = models.TextField(db_column='CommentsWorkplan', blank=True, null=True)
#     commentsbudget = models.TextField(db_column='CommentsBudget', blank=True, null=True)
#     annualreportrcvd = models.DateTimeField(db_column='AnnualReportRcvd', blank=True, null=True)
#     annualreport2drive = models.TextField(db_column='AnnualReport2Drive', blank=True, null=True) This field type is a guess.
#     annualreportcoordinatornotified = models.DateTimeField(db_column='AnnualReportCoordinatorNotified', blank=True, null=True)
#     annualreportdfonotified = models.DateTimeField(db_column='AnnualReportDFONotified', blank=True, null=True)
#     annualreportreturnedtoclient = models.DateTimeField(db_column='AnnualReportReturnedToClient', blank=True, null=True)
#     annualreportreviewstatusnotes = models.CharField(db_column='AnnualReportReviewStatusNotes', max_length=255, blank=True, null=True)
#     annualreportadminnotified = models.DateTimeField(db_column='AnnualReportAdminNotified', blank=True, null=True)
#     annualreportworkplanreviewcomplete = models.DateTimeField(db_column='AnnualReportWorkplanReviewComplete', blank=True, null=True)
#     annualreportfinancialreviewcomplete = models.DateTimeField(db_column='AnnualReportFinancialReviewComplete', blank=True, null=True)
#     annualreportreviewcomplete = models.DateTimeField(db_column='AnnualReportReviewComplete', blank=True, null=True)
#     yearendreportremindertier1 = models.DateTimeField(db_column='YearendReportReminderTier1', blank=True, null=True)
#     yearendreportremindertier2 = models.DateTimeField(db_column='YearendReportReminderTier2', blank=True, null=True)
#     data2accdc = models.TextField(db_column='Data2ACCDC', blank=True, null=True) This field type is a guess.
#     yearendremindersent = models.DateTimeField(db_column='YearEndReminderSent', blank=True, null=True)
#     nwcfstewardshipguide = models.TextField(db_column='NWCFStewardshipGuide', blank=True, null=True) This field type is a guess.
#     surplusemailconfirmationfromclient = models.TextField(db_column='SurplusEmailConfirmationFromClient', blank=True, null=True) This field type is a guess.
#     surplusemailconfirmation2drive = models.TextField(db_column='SurplusEmailConfirmation2Drive', blank=True, null=True) This field type is a guess.
#     surplusadjustannualfunding = models.TextField(db_column='SurplusAdjustAnnualFunding', blank=True, null=True) This field type is a guess.
#     surplusmailcheque2accounting = models.TextField(db_column='SurplusMailCheque2Accounting', blank=True, null=True) This field type is a guess.
#     surplusemailtogcplanning = models.TextField(db_column='SurplusEmailToGCPlanning', blank=True, null=True) This field type is a guess.
#     surpluscheque = models.TextField(db_column='SurplusCheque', blank=True, null=True) This field type is a guess.
#     surpluschequeamount = models.FloatField(db_column='SurplusChequeAmount', blank=True, null=True)
#     surpluspostproject = models.TextField(db_column='SurplusPostProject', blank=True, null=True) This field type is a guess.
#     surplusmidproject = models.TextField(db_column='SurplusMidProject', blank=True, null=True) This field type is a guess.
#     surplusadjustts = models.TextField(db_column='SurplusAdjustTS', blank=True, null=True) This field type is a guess.
#     surplussecretariatsent = models.DateTimeField(db_column='SurplusSecretariatSent', blank=True, null=True)
#     surplussecretariatnotified = models.TextField(db_column='SurplusSecretariatNotified', blank=True, null=True) This field type is a guess.
#     surplusgcaafstep2sent = models.DateTimeField(db_column='SurplusGCAAFStep2Sent', blank=True, null=True)
#     surplusgcaafstep2signed = models.TextField(db_column='SurplusGCAAFStep2Signed', blank=True, null=True) This field type is a guess.
#     surplusamendmentdrafted = models.TextField(db_column='SurplusAmendmentDrafted', blank=True, null=True) This field type is a guess.
#     surpluspackagefmasent = models.DateTimeField(db_column='SurplusPackageFMASent', blank=True, null=True)
#     surpluspackagefmaapproved = models.TextField(db_column='SurplusPackageFMAApproved', blank=True, null=True) This field type is a guess.
#     surplusgcafstep5sent = models.DateTimeField(db_column='SurplusGCAFStep5Sent', blank=True, null=True)
#     surplusgcafstep5signed = models.TextField(db_column='SurplusGCAFStep5Signed', blank=True, null=True) This field type is a guess.
#     surplusamendmentclientsent = models.DateTimeField(db_column='SurplusAmendmentClientSent', blank=True, null=True)
#     surplusamendmentclientsigned = models.TextField(db_column='SurplusAmendmentClientSigned', blank=True, null=True) This field type is a guess.
#     surplusamendmentmanagersent = models.DateTimeField(db_column='SurplusAmendmentManagerSent', blank=True, null=True)
#     surplusamendmentmanagersigned = models.TextField(db_column='SurplusAmendmentManagerSigned', blank=True, null=True) This field type is a guess.
#     surplussignedamendment2client = models.DateTimeField(db_column='SurplusSignedAmendment2Client', blank=True, null=True)
#     surpluspackage2drive = models.TextField(db_column='SurplusPackage2Drive', blank=True, null=True) This field type is a guess.
#     surplussapcommitmentadjsuted = models.TextField(db_column='SurplusSAPCommitmentAdjsuted', blank=True, null=True) This field type is a guess.
#     surplusrecuperatedintime = models.TextField(db_column='SurplusRecuperatedInTime', blank=True, null=True) This field type is a guess.
#     rowversion = models.CharField(db_column='RowVersion', max_length=8, blank=True, null=True)
#
#

# class Tblprojectyearpmt(models.Model):
#     id = models.IntegerField(db_column='ID', blank=True, null=True)
#     oldid = models.IntegerField(db_column='OldID', blank=True, null=True)
#     projectyearid = models.IntegerField(db_column='ProjectYearID', blank=True, null=True)
#     claimnumber = models.IntegerField(db_column='ClaimNumber', blank=True, null=True)
#     currentadvance = models.FloatField(db_column='CurrentAdvance', blank=True, null=True)
#     currentreimbursement = models.FloatField(db_column='CurrentReimbursement', blank=True, null=True)
#     currentdisbursement = models.FloatField(db_column='CurrentDisbursement', blank=True, null=True)
#     claimfrom = models.DateTimeField(db_column='ClaimFrom', blank=True, null=True)
#     claimto = models.DateTimeField(db_column='ClaimTo', blank=True, null=True)
#     finalpayment = models.TextField(db_column='FinalPayment', blank=True, null=True) This field type is a guess.
#     prfcreated = models.TextField(db_column='PRFCreated', blank=True, null=True) This field type is a guess.
#     prfclientsent = models.DateTimeField(db_column='PRFClientSent', blank=True, null=True)
#     prfclientsigned = models.TextField(db_column='PRFClientSigned', blank=True, null=True) This field type is a guess.
#     prfmgrsent = models.DateTimeField(db_column='PRFMgrSent', blank=True, null=True)
#     prfmgrsigned = models.TextField(db_column='PRFMgrSigned', blank=True, null=True) This field type is a guess.
#     fcchecked = models.TextField(db_column='FCChecked', blank=True, null=True) This field type is a guess.
#     prf2drive = models.TextField(db_column='PRF2Drive', blank=True, null=True) This field type is a guess.
#     prfapesent = models.DateTimeField(db_column='PRFAPESent', blank=True, null=True)
#     tsupdated = models.TextField(db_column='TSUpdated', blank=True, null=True) This field type is a guess.
#     sapconfirmed = models.TextField(db_column='SAPConfirmed', blank=True, null=True) This field type is a guess.
#     prf2burlington = models.TextField(db_column='PRF2Burlington', blank=True, null=True) This field type is a guess.
#     clientreferenceno = models.CharField(db_column='ClientReferenceNo', max_length=50, blank=True, null=True)
#     notes = models.TextField(db_column='Notes', blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'TblProjectYearPmt'
