from django.utils.translation import gettext as _

from dm_apps.emails import Email


class NewRecommendationEmail(Email):
    email_template_path = 'res/emails/new_recommendation.html'
    subject_en = 'A new RES promotion application is awaiting your recommendation'
    subject_fr = "Une nouvelle demande de promotion RES attend votre recommandation"

    def get_recipient_list(self):
        return [self.instance.user.email]
