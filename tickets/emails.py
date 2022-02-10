from django.conf import settings

from dm_apps.emails import Email

from_email = settings.SITE_FROM_EMAIL
admin_email = 'DFO.DMApps-ApplisGD.MPO@dfo-mpo.gc.ca'


class NewTicketEmail(Email):
    subject_en = 'new ticket / nouveau billet'
    email_template_path = 'tickets/email_new_ticket.html'

    def get_recipient_list(self):
        return [admin_email]

    def get_subject_fr(self):
        return f'{self.instance.app_display} ({self.instance.get_priority_display()})'


class NewFollowUpEmail(Email):
    subject_en = 'A follow-up has been added to your ticket'
    subject_fr = 'un suivi a été ajouté à votre billet'
    email_template_path = 'tickets/email_follow_up.html'

    def get_recipient_list(self):
        my_to_list = [admin_email]
        if self.instance.ticket.dm_assigned.exists():
            my_to_list.extend([user.email for user in self.instance.ticket.dm_assigned.all()])
        my_to_list.append(self.instance.ticket.primary_contact.email)
        return my_to_list


class TicketResolvedEmail(Email):
    subject_en = 'Your ticket has been resolved'
    subject_fr = 'votre billet a été résolu'
    email_template_path = 'tickets/email_ticket_resolved.html'

    def get_recipient_list(self):
        my_to_list = [self.instance.primary_contact.email]
        return my_to_list
