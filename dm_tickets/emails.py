from django.contrib.auth.models import User
from django.template import loader

from_email = 'DoNotReply@DFOScienceDataManagement.com'
admin_email = 'david.fishman@dfo-mpo.gc.ca'


class NewTicketEmail:
    def __init__(self, object):
        self.subject = 'A new ticket has been created / un nouveau billet a été créé'
        self.message = self.load_html_template(object)
        self.from_email = from_email

        # decide on who should receive the email
        if object.assigned_to:
            self.to_list = [object.assigned_to.email, object.primary_contact.email, ]
        else:
            # get a list of all staff email addresses
            staff_emails = [user.email for user in User.objects.filter(is_staff=True)]
            staff_emails.append(object.primary_contact.email)
            self.to_list = staff_emails

    def load_html_template(self, object):
        t = loader.get_template('dm_tickets/email_new_ticket.html')
        context = {'object': object}
        rendered = t.render(context)
        return rendered

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)


class NewFileAddedEmail:
    def __init__(self, object):
        self.subject = "A new file has been added to Ticket #{}".format(object.ticket.id)
        self.message = self.load_html_template(object)
        self.from_email = from_email
        self.to_list = [admin_email, ]

    def load_html_template(self, object):
        t = loader.get_template('dm_tickets/email_new_file.html')
        context = {'object': object}
        rendered = t.render(context)
        return rendered

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)


class TicketResolvedEmail:

    def __init__(self, ticket_object):
        self.ticket_object = ticket_object
        self.subject = 'Your ticket has been resolved / votre billet a été résolu'
        self.message = self.load_html_template()
        self.from_email = from_email
        # decide on who should receive the email
        if ticket_object.assigned_to:
            self.to_list = [ticket_object.assigned_to.email, ticket_object.primary_contact.email, ]
        else:
            # get a list of all staff email addresses
            staff_emails = [user.email for user in User.objects.filter(is_staff=True)]
            staff_emails.append(ticket_object.primary_contact.email)
            self.to_list = staff_emails

    def load_html_template(self):
        t = loader.get_template('dm_tickets/email_ticket_resolved.html')
        context = {
            'object': self.ticket_object,
        }
        rendered = t.render(context)
        return rendered

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)
