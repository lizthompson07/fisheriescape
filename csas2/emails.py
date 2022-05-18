from django.utils.translation import gettext as _

from dm_apps.emails import Email

csas_generic_email = "csas-sccs@dfo-mpo.gc.ca"


class InvitationEmail(Email):
    email_template_path = 'csas2/emails/invitation.html'
    subject_en = 'You have been invited to attend an event! (*** ACTION REQUIRED ***)'
    subject_fr = "Vous avez été invité à assister à un événement! (*** ACTION REQUISE ***)"

    def get_recipient_list(self):
        return [self.instance.person.email]

    def get_context_data(self):
        context = super().get_context_data()
        field_list = [
            'process',
            'type',
            'location',
            'display_dates|{}'.format(_("dates")),
        ]
        context.update({'event': self.instance, 'field_list': field_list})
        return context


class NewResourceEmail(Email):
    email_template_path = 'csas2/emails/new_resource.html'
    subject_en = 'A new resource is available'
    subject_fr = "Une nouvelle ressource est disponible"

    def get_recipient_list(self):
        return [self.instance.person.email]

    def get_context_data(self):
        context = super().get_context_data()
        field_list = [
            'process',
            'type',
            'location',
            'display_dates|{}'.format(_("dates")),
        ]
        context.update({'object': self.instance, 'resource': self.resource, 'field_list': field_list})
        return context

    def __init__(self, request, instance=None, resource=None):
        super().__init__(request)
        self.request = request
        self.instance = instance
        self.resource = resource


class PublicationNumberRequestEmail(Email):
    email_template_path = 'csas2/emails/pub_number.html'
    subject_en = 'A New publication number is being requested (*** ACTION REQUIRED ***)'

    def get_recipient_list(self):
        return [csas_generic_email]


class PostingRequestEmail(Email):
    email_template_path = 'csas2/emails/posting_request.html'
    subject_en = 'Request to post new CSAS meeting'

    def get_recipient_list(self):
        return [csas_generic_email]


class SoMPEmail(Email):
    email_template_path = 'csas2/emails/somp.html'
    subject_en = 'The SoMP for a meeting has been posted'

    def get_recipient_list(self):
        return [csas_generic_email]


class NewRequestEmail(Email):
    email_template_path = 'csas2/emails/new_request.html'
    subject_en = 'A new CSAS request has been submitted'
    subject_fr = "Une nouvelle demande de SCCS a été soumise"

    def get_recipient_list(self):
        # should go to all emails associated with csas office
        return self.instance.office.all_emails


class ReviewCompleteEmail(Email):
    subject_en = 'A CSAS review has been completed'
    subject_fr = "Un examen du SCAS a été effectué"

    def get_email_template_path(self):
        if self.instance.decision == 1:
            return 'csas2/emails/review_complete_successful.html'
        return 'csas2/emails/review_complete_withdrawn.html'

    def get_recipient_list(self):
        # should go to the client as listed on the original request
        return [self.instance.csas_request.client.email]


class PostedMeetingEmail(Email):
    email_template_path = 'csas2/emails/posted_process.html'
    subject_en = 'Your process has been posted to the CSAS website'
    subject_fr = "Votre processus a été publié sur le site Web du SCCS"

    def get_recipient_list(self):
        # should go to all emails associated with csas office
        return self.instance.process.lead_office.all_emails


class UpdatedMeetingEmail(Email):
    email_template_path = 'csas2/emails/updated_meeting.html'
    subject_en = 'Some information has been updated on a posted meeting'

    def get_recipient_list(self):
        return [csas_generic_email]

    def __init__(self, request, meeting, old_meeting=None, new_expected_publications_en=None, old_expected_publications_en=None,
                 new_expected_publications_fr=None, old_expected_publications_fr=None, new_chair=None, old_chair=None):
        super().__init__(request)
        self.request = request
        self.meeting = meeting
        self.old_meeting = old_meeting
        self.new_expected_publications_en = new_expected_publications_en
        self.old_expected_publications_en = old_expected_publications_en
        self.new_expected_publications_fr = new_expected_publications_fr
        self.old_expected_publications_fr = old_expected_publications_fr
        self.new_chair = new_chair
        self.old_chair = old_chair

    def get_context_data(self):
        context = super().get_context_data()
        old_meeting = self.old_meeting
        if not old_meeting:
            old_meeting = self.meeting
        context.update({
            'old_meeting': old_meeting,
            'meeting': self.meeting,
            'new_expected_publications_en': self.new_expected_publications_en,
            'old_expected_publications_en': self.old_expected_publications_en,
            'new_expected_publications_fr': self.new_expected_publications_fr,
            'old_expected_publications_fr': self.old_expected_publications_fr,
            'new_chair': self.new_chair,
            'old_chair': self.old_chair,
        })
        return context


class ToRReviewAwaitingEmail(Email):
    email_template_path = 'csas2/emails/tor_review_awaiting.html'
    subject_en = "Terms of reference awaiting your review"
    subject_fr = "cadre de référence attend votre avis"

    def get_recipient_list(self):
        return [self.instance.user.email, ]


class ToRChangesRequestedEmail(Email):
    email_template_path = 'csas2/emails/tor_changes_requested.html'
    subject_en = "Changes to ToR required"
    subject_fr = "modifications au cadre de référence sont nécessaires"

    def get_recipient_list(self):
        return self.instance.tor.process.editor_email_list



class ToRPostingRequestEmail(Email):
    email_template_path = 'csas2/emails/tor_posting_request.html'
    subject_en = 'New request to post ToR !!'

    def get_recipient_list(self):
        return [csas_generic_email]



class ToRReviewCompleteEmail(Email):
    email_template_path = 'csas2/emails/tor_review_complete.html'
    subject_en = 'ToR review is complete'
    subject_fr = "l'examen du cadre de référence est terminé"

    def get_recipient_list(self):
        return self.instance.process.editor_email_list


class PostedToREmail(Email):
    email_template_path = 'csas2/emails/tor_posted.html'
    subject_en = 'Your ToR has been posted to the CSAS website'
    subject_fr = "Votre cadre de référence a été publié sur le site Web du SCCS"

    def get_recipient_list(self):
        return self.instance.process.editor_email_list
