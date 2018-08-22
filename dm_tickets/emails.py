from django.template import loader

from_email='DoNotReply@RDMTS.com'
admin_email = 'david.fishman@dfo-mpo.gc.ca'

class NewTicketEmail:
    def __init__(self, object):
        self.subject = 'RDMTS: a new ticket has been created / un nouveau billet a été créé'
        self.message = self.load_html_template(object)
        self.from_email = from_email
        self.to_list = [admin_email,object.primary_contact.email,]

    def load_html_template(self,object):
        t = loader.get_template('tickets/email_new_ticket.html')
        context ={ 'object': object }
        rendered = t.render(context)
        return rendered

class NewFileAddedEmail:
    def __init__(self, object):
        self.subject = "RDMTS: a new file has been added to Ticket #{}".format(object.ticket.id)
        self.message = self.load_html_template(object)
        self.from_email = from_email
        self.to_list = [admin_email,]

    def load_html_template(self,object):
        t = loader.get_template('tickets/email_new_file.html')
        context ={ 'object': object }
        rendered = t.render(context)
        return rendered


class TicketResolvedEmail:

    def __init__(self, ticket_object):
        self.ticket_object = ticket_object
        self.subject = 'RDMTS: Your ticket has been resolved / votre billet a été résolu'
        self.message = self.load_html_template()
        self.from_email = from_email
        self.to_list = [ticket_object.primary_contact.email,]

    def load_html_template(self):
        t = loader.get_template('tickets/email_ticket_resolved.html')
        context ={
            'object': self.ticket_object,
        }
        rendered = t.render(context)
        return rendered
