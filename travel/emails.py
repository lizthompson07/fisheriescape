from django.template import loader

from_email = 'DoNotReply@DMApps.com'


class NewEventEmail:
    def __init__(self, event):
        self.event = event
        self.subject = 'Somebody registered a new event'
        self.message = self.load_html_template()
        self.from_email = from_email
        self.to_list = ["Amelie.Robichaud@dfo-mpo.gc.ca", ]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self):
        t = loader.get_template('travel/email_new_event.html')
        field_list = [
            'name',
            'nom',
            'number',
            'start_date',
            'end_date',
        ]
        print(self.event)
        context = {'event': self.event, 'field_list': field_list}
        rendered = t.render(context)
        return rendered


class AdminApprovalAwaitingEmail:
    def __init__(self, event, approver_field_name):
        user = getattr(event, approver_field_name)
        self.subject = 'A trip is awaiting {} approval'.format(approver_field_name.upper())
        self.message = self.load_html_template(user, event)
        self.from_email = from_email
        self.to_list = ["Amelie.Robichaud@dfo-mpo.gc.ca", "Tracey.Cote@dfo-mpo.gc.ca"]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, user, event):
        t = loader.get_template('travel/email_admin_awaiting_approval.html')

        field_list = [
            'fiscal_year',
            'section',
            'first_name',
            'last_name',
            'trip_title',
            'destination',
            'start_date',
            'end_date',
        ]

        context = {'user': user, 'event': event, 'field_list': field_list}
        rendered = t.render(context)
        return rendered


class ApprovalAwaitingEmail:
    def __init__(self, event, approver_field_name):
        user = getattr(event, approver_field_name)
        self.subject = 'A trip is awaiting your approval'
        self.message = self.load_html_template(user, event)
        self.from_email = from_email
        self.to_list = [user.email, ]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, user, event):
        t = loader.get_template('travel/email_awaiting_approval.html')

        field_list = [
            'fiscal_year',
            'section',
            'first_name',
            'last_name',
            'trip_title',
            'destination',
            'start_date',
            'end_date',
        ]

        context = {'user': user, 'event': event, 'field_list': field_list}
        rendered = t.render(context)
        return rendered
