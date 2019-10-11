from django.template import loader

from_email = 'DoNotReply@DMApps.com'


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
            'user',
            'section',
            'first_name',
            'last_name',
            'address',
            'phone',
            'email',
            'public_servant',
            'company_name',
            'trip_title',
            'departure_location',
            'destination',
            'start_date',
            'end_date',

            # purpose
            'role',
            'reason',
            'purpose',
            'role_of_participant',
            'objective_of_event',
            'benefit_to_dfo',
            'multiple_conferences_rationale',
            'multiple_attendee_rationale',
        ]

        context = {'user': user, 'event': event, 'field_list': field_list}
        rendered = t.render(context)
        return rendered


class UserCreationEmail:
    def __init__(self, object):

        self.subject = 'DM Apps account creation / Création de compte DM Apps'
        self.message = self.load_html_template(object)
        self.from_email = from_email
        self.to_list = ["david.fishman@dfo-mpo.gc.ca"]

        try:
            self.to_list.append(object.email)
        except AttributeError:
            pass

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, object):
        t = loader.get_template('projects/email_user_creation.html')
        context = {'object': object, }
        rendered = t.render(context)
        return rendered
