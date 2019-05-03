import datetime
import os

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
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

    path_number = models.CharField(max_length=50, blank=True, null=True)
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


class ContributionAgreementChecklist(models.Model):
    project = models.OneToOneField(Project, on_delete=models.DO_NOTHING, related_name="ca_checklist")
    risk_assessment_complete = models.NullBooleanField(verbose_name=_("The risk assessment has been completed/approved and posted to PATH"))
    correct_clause_selected =  models.NullBooleanField(verbose_name=_("The clauses selected in the CA reflect the risk level and contribution amount"))
    formatting_correct =  models.NullBooleanField(verbose_name=_("There are no hanging/orphan lines/titles"))
    amounts_correct =  models.NullBooleanField(verbose_name=_("The annual contribution amount(s) (3.1) match(es) the budget in Schedule 5 and do(es) not exceed the amount(s) approved by the Minister"))
    clear_language =  models.NullBooleanField(verbose_name=_("Schedule 5: Language is clear, concise and can be generally understood by someone who is not a specialist"))
    acronyms_defined =  models.NullBooleanField(verbose_name=_("Schedule 5: Acronyms are defined upon first use"))
    activities_elibigle =  models.NullBooleanField(verbose_name=_("Schedule 5: All Activities/tasks are eligible"))
    detail_commensurate_with_budget =  models.NullBooleanField(verbose_name=_("Schedule 5: The level of detail for each Activity (i.e., task description) is commensurate with its budget"))
    realistic_timeframe =  models.NullBooleanField(verbose_name=_("Schedule 5: Each Activity can be reasonably expected to be completed within its accorded timeframe"))
    key_tasks_outlined =  models.NullBooleanField(verbose_name=_("Schedule 5: All key tasks required to be undertaken for each Activity to be achieved are outlined"))
    deliverables =  models.NullBooleanField(verbose_name=_("Schedule 5: All Activities/tasks have associated deliverables that will demonstrate that the former were completed as planned and as budgeted"))
    project_budgets_adds_up =  models.NullBooleanField(verbose_name=_("Schedule 5: The sum of all individual project Activity budgets adds up to the agreement total"))
    sufficient_budget_detail =  models.NullBooleanField(verbose_name=_("Schedule 5: Sufficient budget details have been provided to confirm that the costs are eligible and reasonable"))
    expenses_eligible =  models.NullBooleanField(verbose_name=_("Schedule 5: All expenses are eligible"))
    reasonable_costs =  models.NullBooleanField(verbose_name=_("Schedule 5: All costs are reasonable"))
    budget_adds_up =  models.NullBooleanField(verbose_name=_("Schedule 5: The budget adds up correctly."))
    maximum_amounts_set =  models.NullBooleanField(verbose_name=_("Schedule 5: If applicable, maximum amounts for expense categories have been set (i.e., identified with an asterisk (*))."))
    budget_reflects_activity =  models.NullBooleanField(verbose_name=_("Schedule 5: The budget reflects the nature of the Activity(ies)."))
    stacking_limits_respected =  models.NullBooleanField(verbose_name=_("Schedule 5: The federal and stacking limit have been respected, based on confirmed funding."))
    no_funding_redundancy =  models.NullBooleanField(verbose_name=_("Schedule 5: The activities and budget items have been cross-checked against DFO Aboriginal program CAs (e.g., SPI-FHRI, AAROM, AFSAR) to ensure no funding redundancy."))
    stacking_identified =  models.NullBooleanField(verbose_name=_("Schedule 5: Funding directly related to the RFCPP project coming from DFO Aboriginal programs has been included in the federal and stacking support."))
    confirmation_letters_2_path =  models.NullBooleanField(verbose_name=_("Schedule 5: Confirmation letters for all confirmed cash support have been posted to PATH.  Confirmation letters for large amount/potentially inflated in-kind support have also been posted to PATH."))
    financial_information_2_path =  models.NullBooleanField(verbose_name=_("Schedule 5: Financial information has been updated/entered in PATH as per Data Entry Procedures"))
    conflict_of_interest_assessed =  models.NullBooleanField(verbose_name=_("Schedule 5: If a current or former federal public servant is involved in the project, a conflict of interest assessment has been completed (conflict of interest assessment tool found in CA checklist folder in national shared folder) and conflicts, if any, have been addressed, as appropriate."))
    # Schedule 6
    cashflow_adds_up =  models.NullBooleanField(verbose_name=_("Schedule 6: The cash flow adds up correctly and reflects the timing of Activities."))
    # Schedule 7
    pre_filled_sched7 =  models.NullBooleanField(verbose_name=_("Schedule 7: is pre-filled and mirrors Schedule 5"))
    performance_measures_in_path =  models.NullBooleanField(verbose_name=_("Schedule 7: Performance measures are updated in the ‘Planned’ column of the performance tab in PATH as per Data Entry Procedures"))
    # General
    team_leader_reviewed =  models.NullBooleanField(verbose_name=_("The Team Leader has reviewed and approves the CA"))
    comment_for_nhq =  models.TextField(verbose_name=_("Comments for NHQ"), blank=True, null=True)

"""



"""




def draft_ca_file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/entry_<id>/<filename>
    suffix = filename.split(".")[1]
    return 'spot/{0}/{0}_draft_contribution_agreement.{1}'.format(instance.id, suffix)


class ProjectYear(models.Model):

    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name="projects", verbose_name=_("project language"))
    fiscal_year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, related_name="projects")
    expenditure_initiation_date = models.DateTimeField(blank=True, null=True, default=datetime.datetime(timezone.now().year, 4, 1))
    paye_number = models.CharField(max_length=50, blank=True, null=True)
    annual_funding = models.FloatField(blank=True, null=True)
    initiation_date = models.DateTimeField(blank=True, null=True)
    initiation_type = models.ForeignKey(InitiationType, on_delete=models.DO_NOTHING, related_name="projects")
    initiation_acknowledgement_sent = models.DateTimeField(blank=True, null=True)
    eoi_coordinator_notified = models.DateTimeField(blank=True, null=True)
    eoi_feedback_sent = models.DateTimeField(blank=True, null=True)
    negotiation_letter_sent = models.DateTimeField(blank=True, null=True)
    schedule_5_complete = models.DateTimeField(blank=True, null=True)
    advance_payment = models.BooleanField(default=False)
    draft_ca_sent_to_proponent = models.DateTimeField(blank=True, null=True)
    draft_ca_proponent_approved = models.DateTimeField(blank=True, null=True)
    draft_ca_ready = models.DateTimeField(blank=True, null=True)

    # CA Checklist stuff


    ca_checklist_complete = models.DateTimeField(blank=True, null=True) # this field might be redundant
    draft_ca_sent_to_manager = models.DateTimeField(blank=True, null=True, verbose_name=_("draft CA sent to manager"))
    draft_ca_manager_approved = models.DateTimeField(blank=True, null=True, verbose_name=_("draft CA approved by manager"))
    draft_ca = models.FileField(verbose_name=_("draft CA"))
    draft_ca_sent_to_nhq = models.DateTimeField(blank=True, null=True, verbose_name=_("draft CA sent to NHQ"))
    aip_received = models.DateTimeField(blank=True, null=True, verbose_name=_("approve-in-principal (AIP) received"))
    final_ca_received = models.DateTimeField(blank=True, null=True)
    final_ca_sent_to_proponent = models.DateTimeField(blank=True, null=True)
    final_ca_proponent_signed = models.DateTimeField(blank=True, null=True)
    final_ca_sent_to_NHQ = models.DateTimeField(blank=True, null=True)
    advance_payment_sent_to_NHQ = models.DateTimeField(blank=True, null=True)
    final_ca_NHQ_signed = models.DateTimeField(blank=True, null=True)


    # camgrsigned = models.DateTimeField(db_column='CAMgrSigned', blank=True, null=True)
    # caprfmgrsent = models.DateTimeField(db_column='CAPRFMgrSent', blank=True, null=True)
    # caprfclientsent = models.DateTimeField(db_column='CAPRFClientSent', blank=True, null=True)
    # caclientsigned = models.TextField(db_column='CAClientSigned', blank=True, null=True) This field type is a guess.
    # catemplate2drive = models.TextField(db_column='CATemplate2Drive', blank=True, null=True) This field type is a guess.
    # ca2drive = models.DateTimeField(db_column='CA2Drive', blank=True, null=True)
    # completedcaclientsent = models.DateTimeField(db_column='CompletedCAClientSent', blank=True, null=True)
    # gcaffmaapproved = models.DateTimeField(db_column='GCAFFMAApproved', blank=True, null=True)
    # gcaffmasent = models.DateTimeField(db_column='GCAFFMASent', blank=True, null=True)
    # gcafmgrsigned = models.TextField(db_column='GCAFMgrSigned', blank=True, null=True) This field type is a guess.
    # gcaframgrsent = models.DateTimeField(db_column='GCAFRAMgrSent', blank=True, null=True)
    # gcaf2drive = models.TextField(db_column='GCAF2Drive', blank=True, null=True) This field type is a guess.
    # gcafupdated = models.TextField(db_column='GCAFUpdated', blank=True, null=True) This field type is a guess.
    # lon2drive = models.TextField(db_column='LoN2Drive', blank=True, null=True) This field type is a guess.
    # olaready = models.TextField(db_column='OLAReady', blank=True, null=True) This field type is a guess.
    # prfmgrsigned = models.TextField(db_column='PRFMgrSigned', blank=True, null=True) This field type is a guess.
    # prfready = models.TextField(db_column='PRFReady', blank=True, null=True) This field type is a guess.
    # prfapesent = models.DateTimeField(db_column='PRFAPESent', blank=True, null=True)
    # prfclientsigned = models.TextField(db_column='PRFClientSigned', blank=True, null=True) This field type is a guess.
    # prf2drive = models.TextField(db_column='PRF2Drive', blank=True, null=True) This field type is a guess.
    # ramgrsigned = models.TextField(db_column='RAMgrSigned', blank=True, null=True) This field type is a guess.
    # ra2drive = models.TextField(db_column='RA2Drive', blank=True, null=True) This field type is a guess.
    # amendmentsent = models.DateTimeField(db_column='AmendmentSent', blank=True, null=True)
    # annualcashflowapproved = models.TextField(db_column='AnnualCashflowApproved', blank=True, null=True) This field type is a guess.
    # annualcashflowready = models.DateTimeField(db_column='AnnualCashflowReady', blank=True, null=True)
    # workplanreviewcomplete = models.DateTimeField(db_column='WorkplanReviewComplete', blank=True, null=True)
    # financialreviewcomplete = models.DateTimeField(db_column='FinancialReviewComplete', blank=True, null=True)
    # myupdatercvd = models.DateTimeField(db_column='MYUpdateRcvd', blank=True, null=True)
    # myupdateadminnotified = models.DateTimeField(db_column='MYUpdateAdminNotified', blank=True, null=True)
    # pamyupdatechanges2financialsid = models.IntegerField(db_column='PAMYUpdateChanges2FinancialsID', blank=True, null=True)
    # pamyupdatechanges2workplanid = models.IntegerField(db_column='PAMYUpdateChanges2WorkplanID', blank=True, null=True)
    # myupdatereviewcomplete = models.DateTimeField(db_column='MYUpdateReviewComplete', blank=True, null=True)
    # lonsavedaspdf = models.TextField(db_column='LoNSavedAsPDF', blank=True, null=True) This field type is a guess.
    # casavedaspdf = models.TextField(db_column='CASavedAsPDF', blank=True, null=True) This field type is a guess.
    # gcafsavedaspdf = models.TextField(db_column='GCAFSavedAsPDF', blank=True, null=True) This field type is a guess.
    # notifyadmin = models.DateTimeField(db_column='NotifyAdmin', blank=True, null=True)
    # appendixeaspdf = models.TextField(db_column='AppendixEAsPDF', blank=True, null=True) This field type is a guess.
    # rasavedaspdf = models.TextField(db_column='RASavedAsPDF', blank=True, null=True) This field type is a guess.
    # auditrcvd = models.DateTimeField(db_column='AuditRcvd', blank=True, null=True)
    # coordinatornotes = models.TextField(db_column='CoordinatorNotes', blank=True, null=True)
    # forecastingnotes = models.TextField(db_column='ForecastingNotes', blank=True, null=True)
    # forecastingflagged = models.TextField(db_column='ForecastingFlagged', blank=True, null=True) This field type is a guess.
    # qr3emailsent = models.DateTimeField(db_column='QR3EmailSent', blank=True, null=True)
    # qr3reminder = models.DateTimeField(db_column='QR3Reminder', blank=True, null=True)
    # qr3forecastcomplete = models.DateTimeField(db_column='QR3ForecastComplete', blank=True, null=True)
    # qr3forecastresponseid = models.IntegerField(db_column='QR3ForecastResponseID', blank=True, null=True)
    # qr3forecastresponsedate = models.DateTimeField(db_column='QR3ForecastResponseDate', blank=True, null=True)
    # qr3interimreportdate = models.DateTimeField(db_column='QR3InterimReportDate', blank=True, null=True)
    # qr3interimreportreviewed = models.DateTimeField(db_column='QR3InterimReportReviewed', blank=True, null=True)
    # qr3interimreportapproved = models.DateTimeField(db_column='QR3InterimReportApproved', blank=True, null=True)
    # qr3interimreport2drive = models.TextField(db_column='QR3InterimReport2Drive', blank=True, null=True) This field type is a guess.
    # qr3payment = models.TextField(db_column='QR3Payment', blank=True, null=True) This field type is a guess.
    # qr3paymentclaim = models.IntegerField(db_column='QR3PaymentClaim', blank=True, null=True)
    # qr4emailsent = models.DateTimeField(db_column='QR4EmailSent', blank=True, null=True)
    # qr4reminder = models.DateTimeField(db_column='QR4Reminder', blank=True, null=True)
    # qr4forecastcomplete = models.DateTimeField(db_column='QR4ForecastComplete', blank=True, null=True)
    # qr4forecastresponseid = models.IntegerField(db_column='QR4ForecastResponseID', blank=True, null=True)
    # qr4forecastresponsedate = models.DateTimeField(db_column='QR4ForecastResponseDate', blank=True, null=True)
    # qr4payment = models.TextField(db_column='QR4Payment', blank=True, null=True) This field type is a guess.
    # qr4paymentclaim = models.IntegerField(db_column='QR4PaymentClaim', blank=True, null=True)
    # commentsfromboard = models.TextField(db_column='CommentsFromBoard', blank=True, null=True)
    # commentsworkplan = models.TextField(db_column='CommentsWorkplan', blank=True, null=True)
    # commentsbudget = models.TextField(db_column='CommentsBudget', blank=True, null=True)
    # annualreportrcvd = models.DateTimeField(db_column='AnnualReportRcvd', blank=True, null=True)
    # annualreport2drive = models.TextField(db_column='AnnualReport2Drive', blank=True, null=True) This field type is a guess.
    # annualreportcoordinatornotified = models.DateTimeField(db_column='AnnualReportCoordinatorNotified', blank=True, null=True)
    # annualreportdfonotified = models.DateTimeField(db_column='AnnualReportDFONotified', blank=True, null=True)
    # annualreportreturnedtoclient = models.DateTimeField(db_column='AnnualReportReturnedToClient', blank=True, null=True)
    # annualreportreviewstatusnotes = models.CharField(db_column='AnnualReportReviewStatusNotes', max_length=255, blank=True, null=True)
    # annualreportadminnotified = models.DateTimeField(db_column='AnnualReportAdminNotified', blank=True, null=True)
    # annualreportworkplanreviewcomplete = models.DateTimeField(db_column='AnnualReportWorkplanReviewComplete', blank=True, null=True)
    # annualreportfinancialreviewcomplete = models.DateTimeField(db_column='AnnualReportFinancialReviewComplete', blank=True, null=True)
    # annualreportreviewcomplete = models.DateTimeField(db_column='AnnualReportReviewComplete', blank=True, null=True)
    # yearendreportremindertier1 = models.DateTimeField(db_column='YearendReportReminderTier1', blank=True, null=True)
    # yearendreportremindertier2 = models.DateTimeField(db_column='YearendReportReminderTier2', blank=True, null=True)
    # data2accdc = models.TextField(db_column='Data2ACCDC', blank=True, null=True) This field type is a guess.
    # yearendremindersent = models.DateTimeField(db_column='YearEndReminderSent', blank=True, null=True)
    # nwcfstewardshipguide = models.TextField(db_column='NWCFStewardshipGuide', blank=True, null=True) This field type is a guess.
    # surplusemailconfirmationfromclient = models.TextField(db_column='SurplusEmailConfirmationFromClient', blank=True, null=True) This field type is a guess.
    # surplusemailconfirmation2drive = models.TextField(db_column='SurplusEmailConfirmation2Drive', blank=True, null=True) This field type is a guess.
    # surplusadjustannualfunding = models.TextField(db_column='SurplusAdjustAnnualFunding', blank=True, null=True) This field type is a guess.
    # surplusmailcheque2accounting = models.TextField(db_column='SurplusMailCheque2Accounting', blank=True, null=True) This field type is a guess.
    # surplusemailtogcplanning = models.TextField(db_column='SurplusEmailToGCPlanning', blank=True, null=True) This field type is a guess.
    # surpluscheque = models.TextField(db_column='SurplusCheque', blank=True, null=True) This field type is a guess.
    # surpluschequeamount = models.FloatField(db_column='SurplusChequeAmount', blank=True, null=True)
    # surpluspostproject = models.TextField(db_column='SurplusPostProject', blank=True, null=True) This field type is a guess.
    # surplusmidproject = models.TextField(db_column='SurplusMidProject', blank=True, null=True) This field type is a guess.
    # surplusadjustts = models.TextField(db_column='SurplusAdjustTS', blank=True, null=True) This field type is a guess.
    # surplussecretariatsent = models.DateTimeField(db_column='SurplusSecretariatSent', blank=True, null=True)
    # surplussecretariatnotified = models.TextField(db_column='SurplusSecretariatNotified', blank=True, null=True) This field type is a guess.
    # surplusgcaafstep2sent = models.DateTimeField(db_column='SurplusGCAAFStep2Sent', blank=True, null=True)
    # surplusgcaafstep2signed = models.TextField(db_column='SurplusGCAAFStep2Signed', blank=True, null=True) This field type is a guess.
    # surplusamendmentdrafted = models.TextField(db_column='SurplusAmendmentDrafted', blank=True, null=True) This field type is a guess.
    # surpluspackagefmasent = models.DateTimeField(db_column='SurplusPackageFMASent', blank=True, null=True)
    # surpluspackagefmaapproved = models.TextField(db_column='SurplusPackageFMAApproved', blank=True, null=True) This field type is a guess.
    # surplusgcafstep5sent = models.DateTimeField(db_column='SurplusGCAFStep5Sent', blank=True, null=True)
    # surplusgcafstep5signed = models.TextField(db_column='SurplusGCAFStep5Signed', blank=True, null=True) This field type is a guess.
    # surplusamendmentclientsent = models.DateTimeField(db_column='SurplusAmendmentClientSent', blank=True, null=True)
    # surplusamendmentclientsigned = models.TextField(db_column='SurplusAmendmentClientSigned', blank=True, null=True) This field type is a guess.
    # surplusamendmentmanagersent = models.DateTimeField(db_column='SurplusAmendmentManagerSent', blank=True, null=True)
    # surplusamendmentmanagersigned = models.TextField(db_column='SurplusAmendmentManagerSigned', blank=True, null=True) This field type is a guess.
    # surplussignedamendment2client = models.DateTimeField(db_column='SurplusSignedAmendment2Client', blank=True, null=True)
    # surpluspackage2drive = models.TextField(db_column='SurplusPackage2Drive', blank=True, null=True) This field type is a guess.
    # surplussapcommitmentadjsuted = models.TextField(db_column='SurplusSAPCommitmentAdjsuted', blank=True, null=True) This field type is a guess.
    # surplusrecuperatedintime = models.TextField(db_column='SurplusRecuperatedInTime', blank=True, null=True) This field type is a guess.
    # rowversion = models.CharField(db_column='RowVersion', max_length=8, blank=True, null=True)



@receiver(models.signals.post_delete, sender=ProjectYear)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """

    # for draft ca
    if instance.draft_ca:
        if os.path.isfile(instance.draft_ca.path):
            os.remove(instance.draft_ca.path)


@receiver(models.signals.pre_save, sender=ProjectYear)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    # for draft ca
    try:
        old_file = ProjectYear.objects.get(pk=instance.pk).draft_ca
    except ProjectYear.DoesNotExist:
        return False

    new_file = instance.draft_ca
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


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
