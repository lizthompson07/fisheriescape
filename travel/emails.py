from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.template import loader
from django.utils.translation import activate, get_language

from dm_apps.context_processor import my_envr
from dm_apps.emails import Email

from_email = settings.SITE_FROM_EMAIL

request_field_list = [
    'fiscal_year',
    'section',
    'created_by',
    'trip',
]

trip_field_list = [
    'fiscal_year',
    'name',
    'nom',
    'lead',
    'is_adm_approval_required',
    'location',
    'start_date',
    'end_date',
]


class NewTripEmail:
    def __init__(self, event, request):
        self.event = event
        self.request = request
        self.subject = 'Somebody created a new trip'
        self.message = self.load_html_template()
        self.from_email = from_email
        if event.is_adm_approval_required:
            self.to_list = [user.email for user in User.objects.filter(groups__name="travel_adm_admin")]
            self.subject += ' - ADM verification needed'
        else:
            adm_admins = [user.id for user in User.objects.filter(groups__name="travel_adm_admin")]
            self.to_list = [user.email for user in User.objects.filter(groups__name="travel_admin").filter(~Q(id__in=adm_admins))]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self):
        t = loader.get_template('travel/emails/email_new_event.html')
        field_list = trip_field_list
        context = {'event': self.event, 'field_list': field_list}
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered


class RDGReviewAwaitingEmail:
    def __init__(self, trip_request, reviewer, request):
        self.request = request
        self.subject = 'A trip request is awaiting {} approval'.format(reviewer.get_role_display())
        self.message = self.load_html_template(trip_request, reviewer)
        self.from_email = from_email
        self.to_list = [user.email for user in User.objects.filter(groups__name="travel_admin")]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, trip_request, reviewer):
        t = loader.get_template('travel/emails/email_admin_awaiting_approval.html')

        field_list = request_field_list

        context = {'triprequest': trip_request, 'reviewer': reviewer, 'field_list': field_list}
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered


class ReviewAwaitingEmail(Email):
    email_template_path = 'travel/emails/email_awaiting_review.html'

    def get_subject_en(self):
        return 'A LATE trip request is awaiting your review' if self.instance.is_late_request else 'A trip request is awaiting your review'

    def get_subject_fr(self):
        return 'Une demande de voyage TARDIVE attend votre examen' if self.instance.is_late_request else 'Une demande de voyage attend votre examenw'

    def get_recipient_list(self):
        return [self.reviewer.user.email, ]

    def get_context_data(self):
        context = super().get_context_data()
        context.update({'reviewer': self.reviewer, 'triprequest': self.instance, 'field_list': request_field_list})
        return context

    def __init__(self, request, instance=None, reviewer=None):
        super().__init__(request)
        self.request = request
        self.instance = instance
        self.reviewer = reviewer


class TripReviewAwaitingEmail:
    def __init__(self, trip_object, reviewer_object, request):
        self.request = request
        self.subject = 'A trip is awaiting your review - un voyage attend votre avis'
        self.message = self.load_html_template(trip_object, reviewer_object)
        self.from_email = from_email
        self.to_list = [reviewer_object.user.email, ]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, trip_object, reviewer_object):
        t = loader.get_template('travel/emails/email_awaiting_trip_review.html')
        field_list = trip_field_list
        context = {'reviewer': reviewer_object, 'trip': trip_object, 'field_list': field_list}
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered


class ChangesRequestedEmail:
    def __init__(self, trip_request_object, request):
        self.request = request
        self.subject = 'Changes to your trip request are required - des modifications à votre demande de voyage sont nécessaires'
        self.message = self.load_html_template(trip_request_object)
        self.from_email = from_email
        self.to_list = [trip_request_object.created_by.email, ]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, trip_request_object):
        t = loader.get_template('travel/emails/email_changes_requested.html')

        field_list = request_field_list

        context = {'triprequest': trip_request_object, 'field_list': field_list}
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered


class StatusUpdateEmail:
    def __init__(self, trip_request_object, request):
        self.request = request
        lang = get_language()
        activate('en')
        self.subject = 'Your trip request has been ' + str(trip_request_object.get_status_display())
        activate('fr')
        self.subject += " - Votre demande de voyage a été " + str(trip_request_object.get_status_display())
        activate(lang)
        self.message = self.load_html_template(trip_request_object)
        self.from_email = from_email
        to_list = [trip_request_object.created_by.email, ]
        to_list.extend([t.email for t in trip_request_object.travellers.all()])
        self.to_list = to_list

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, trip_request_object):
        t = loader.get_template('travel/emails/email_status_update.html')
        field_list = request_field_list
        context = {'triprequest': trip_request_object, 'field_list': field_list}
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered


class RemovedTravellerEmail:
    def __init__(self, traveller, request):
        self.request = request
        self.subject = "You have been removed from a request - Vous avez été retiré d'une demande"
        self.message = self.load_html_template(traveller)
        self.from_email = from_email
        self.to_list = [traveller.email, ]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, traveller):
        t = loader.get_template('travel/emails/email_traveller_removed.html')
        field_list = request_field_list
        context = {'traveller': traveller, 'field_list': field_list}
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered


class TripCostWarningEmail:

    def __init__(self, trip, request):
        self.request = request
        self.subject = '*** Trip cost warning / Avertissement de coût de voyage ***'
        self.message = self.load_html_template(trip)
        self.from_email = from_email

        travel_admin_list = [user.email for user in User.objects.filter(groups__name="travel_admin")]
        travel_admin_list.append("DFO.ScienceTravel-VoyagesSciences.MPO@dfo-mpo.gc.ca")
        self.to_list = travel_admin_list

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, trip_request_object):
        t = loader.get_template('travel/emails/email_trip_cost_warning.html')

        field_list = trip_field_list

        context = {'trip': trip_request_object, 'field_list': field_list}
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered
