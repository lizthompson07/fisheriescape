from django.utils.translation import gettext as _

from dm_apps.emails import Email


class NewRecommendationEmail(Email):
    email_template_path = 'res/emails/new_recommendation.html'
    subject_en = 'A new RES promotion application is awaiting your recommendation'
    subject_fr = "Une nouvelle demande de promotion RES attend votre recommandation"

    def get_recipient_list(self):
        return [self.instance.application.manager.email]


class SignatureAwaitingEmail(Email):
    email_template_path = 'res/emails/signature_awaiting.html'
    subject_en = 'A RES promotion application is awaiting your signature'
    subject_fr = "Une demande de promotion RES attend votre signature"

    def get_recipient_list(self):
        return [self.instance.application.applicant.email]
