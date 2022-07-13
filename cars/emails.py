from django.utils.translation import gettext as _

from dm_apps.emails import Email


class RSVPEmail(Email):
    email_template_path = 'cars/emails/rsvp.html'
    subject_en = 'Vehicle reservation request (*** ACTION REQUIRED ***)'
    subject_fr = "Demande de réservation de véhicule (*** ACTION REQUISE ***)"

    def get_recipient_list(self):
        return [self.instance.vehicle.custodian.email]

    def get_context_data(self):
        context = super().get_context_data()
        field_list = [
            "status",
            "vehicle",
            "vehicle.custodian|{}".format(_("custodian")),
            "destination",
            "primary_driver",
            "start_date",
            "end_date",
            "other_drivers",
            "comments",
        ]
        context.update({'field_list': field_list})
        return context


class ApprovedEmail(RSVPEmail):
    email_template_path = 'cars/emails/notification.html'
    subject_en = 'Your vehicle reservation request was approved'
    subject_fr = "votre réservation de véhicule a été approuvée"

    def get_recipient_list(self):
        return [self.instance.primary_driver.email]

    def get_context_data(self):
        context = super().get_context_data()
        context['action_en'] = "approved"
        context['action_fr'] = "approuvée"
        return context


class DeniedEmail(ApprovedEmail):
    subject_en = 'Your vehicle reservation request was denied'
    subject_fr = "votre réservation de véhicule a été refusée"

    def get_context_data(self):
        context = super().get_context_data()
        context['action_en'] = "denied"
        context['action_fr'] = "refusée"
        return context
