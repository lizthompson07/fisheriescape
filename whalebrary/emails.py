from dm_apps import settings
from dm_apps.emails import Email
from dm_apps.utils import custom_send_mail

glfwhale_generic_email = "dfo.glfwhales-baleinesglf.mpo@dfo-mpo.gc.ca"


class NewIncidentEmail(Email):

    email_template_path = 'whalebrary/email_incident.html'
    recipient_list = ["WhaleSightings.XMAR@dfo-mpo.gc.ca",
                        "DFO.GLFWhales-BaleinesGLF.MPO@dfo-mpo.gc.ca"
                    ]

    def get_subject(self):

        return '{} - {} - {}'.format(self.instance.get_incident_type_display(), self.instance.species,
                          self.instance.first_report.strftime("%B %d, %Y @ %I:%M %p %Z"))


class NewResightEmail(Email):

    email_template_path = 'whalebrary/email_resight.html'
    recipient_list = ["WhaleSightings.XMAR@dfo-mpo.gc.ca",
                        "DFO.GLFWhales-BaleinesGLF.MPO@dfo-mpo.gc.ca"
                    ]

    def get_subject(self):

        return 'RESIGHTING {} - {}'.format(self.instance.incident, self.instance.resight_date.strftime("%B %d, %Y @ %I:%M %p %Z"))

# class NewIncidentEmail:
#
#     def __init__(self, incident_object, request):
#         self.request = request
#         # self.subject = self.subject_template(incident_object)
#         self.message = self.load_html_template(incident_object)
#         self.from_email = from_email
#         self.to_list = ["WhaleSightings.XMAR@dfo-mpo.gc.ca",
#                         "DFO.GLFWhales-BaleinesGLF.MPO@dfo-mpo.gc.ca"
#                         ]
#
    # def load_html_template(self, incident_object):
    #     t = loader.get_template('whalebrary/email_incident.html')
    #     context = {'object': incident_object}
    #     context.update(my_envr(self.request))
    #     rendered = t.render(context)
    #     return rendered
#
#
#     def subject_template(self, incident_object):
#         t = loader.get_template('whalebrary/email_incident_subject.html')
#         context = {'object': incident_object}
#         context.update(my_envr(self.request))
#         rendered = t.render(context)
#         return rendered
#
#     def __str__(self):
#         return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject,
#                                                                   self.message)


class MaintenanceReminderEmail(Email):
    email_template_path = 'whalebrary/email_maintenance_reminder.html'

    def get_subject_en(self):
        if self.instance.item:
            mystr = f"MAINTENANCE REMINDER for {self.instance.item}"
        else:
            mystr = "MAINTENANCE REMINDER"
        return mystr

    def get_subject_fr(self):
        if self.instance.item:
            mystr = f"RAPPEL D'ENTRETIEN pour {self.instance.item}"
        else:
            mystr = "RAPPEL D'ENTRETIEN"
        return mystr

    def get_recipient_list(self):
        payload = [glfwhale_generic_email, self.instance.assigned_to.email]
        return payload

    def __init__(self, instance=None):
        self.instance = instance

    def get_context_data(self):
        context = dict()
        context["object"] = self.instance
        context["SITE_FULL_URL"] = settings.SITE_FULL_URL
        return context

    def send(self):
        custom_send_mail(
            email_instance=self,
            user=self.instance.assigned_to
        )
