from django.contrib.auth.models import User
from django.template import loader

from_email = 'DoNotReply@DMApps.com'


class NewTripEmail:
    def __init__(self, event):
        self.event = event
        self.subject = 'Somebody created a new trip'
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
    def __init__(self, trip_request):
        self.subject = 'A trip request is awaiting {} approval'.format(trip_request.current_reviewer.role)
        self.message = self.load_html_template(trip_request)
        self.from_email = from_email
        self.to_list = [user.email for user in User.objects.filter(groups__name="travel_admin")]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, trip_request):
        t = loader.get_template('travel/email_admin_awaiting_approval.html')

        field_list = [
            'fiscal_year',
            'section',
            'first_name',
            'last_name',
            'conference',
            'destination',
            'start_date',
            'end_date',
        ]

        context = {'triprequest': trip_request, 'field_list': field_list}
        rendered = t.render(context)
        return rendered


class ReviewAwaitingEmail:
    def __init__(self, trip_request_object, reviewer_object):
        self.subject = 'A trip request is awaiting your review - un voyage attend votre avis'
        self.message = self.load_html_template(trip_request_object, reviewer_object)
        self.from_email = from_email
        self.to_list = [reviewer_object.user.email, ]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, trip_request_object, reviewer_object):
        t = loader.get_template('travel/email_awaiting_review.html')

        field_list = [
            'fiscal_year',
            'section',
            'user',
            'conference',
            'destination',
            'start_date',
            'end_date',
        ]

        context = {'reviewer': reviewer_object, 'triprequest': trip_request_object, 'field_list': field_list}
        rendered = t.render(context)
        return rendered



class ChangesRequestedEmail:
    def __init__(self, trip_request_object):
        self.subject = 'Changes to your trip request are required - des modifications à votre voyage sont nécessaires'
        self.message = self.load_html_template(trip_request_object)
        self.from_email = from_email
        self.to_list = [trip_request_object.user.email, ]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, trip_request_object):
        t = loader.get_template('travel/email_changes_requested.html')

        field_list = [
            'fiscal_year',
            'section',
            'user',
            'conference',
            'destination',
            'start_date',
            'end_date',
        ]

        context = {'triprequest': trip_request_object, 'field_list': field_list}
        rendered = t.render(context)
        return rendered


class StatusUpdateEmail:
    def __init__(self, trip_request_object):

        self.subject = 'Your trip request has been ' + trip_request_object.status.name + " - Votre demande de voyage a été " + trip_request_object.status.nom
        self.message = self.load_html_template(trip_request_object)
        self.from_email = from_email
        self.to_list = [trip_request_object.user.email, ]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, trip_request_object):
        t = loader.get_template('travel/email_status_update.html')

        field_list = [
            'fiscal_year',
            'section',
            'user',
            'conference',
            'destination',
            'start_date',
            'end_date',
        ]

        context = {'triprequest': trip_request_object, 'field_list': field_list}
        rendered = t.render(context)
        return rendered