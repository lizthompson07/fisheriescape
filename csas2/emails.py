from django.template import loader
from django.utils.translation import gettext as _

from dm_apps.context_processor import my_envr
from dm_apps.emails import Email
from lib.functions.custom_functions import listrify


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




class NewResourceEmail:
    def __init__(self, invitee, resource, request):
        self.request = request
        self.subject = "A new resource is available  / " \
                       "Une nouvelle ressource est disponible"
        self.message = self.load_html_template(invitee, resource)
        self.from_email = invitee.event.from_email
        self.to_list = [invitee.email]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def to_dict(self):
        return {
            "from": self.from_email,
            "to": listrify(self.to_list),
            "subject": self.subject,
            "message": self.message
        }

    def load_html_template(self, invitee, resource):
        t = loader.get_template('events/emails/new_resource.html')
        field_list = [
            'tname|{}'.format("name"),
            'display_dates|{}'.format(_("dates")),
            'location',
            'proponent',
            'type',
        ]
        context = {'invitee': invitee, "field_list": field_list, "resource": resource}
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered
