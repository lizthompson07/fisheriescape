from django.conf import settings
from django.template import loader
from . import models


app_name = settings.WEB_APP_NAME # should be a single word with one space
from_email='DoNotReply@{}.com'.format(app_name)
admin_email = 'david.fishman@dfo-mpo.gc.ca'

class CertificationRequestEmail:

    def __init__(self, person_object):
        self.person_object = person_object
        self.subject = 'Your metadata inventory'
        self.message = self.load_html_template()
        self.from_email = admin_email
        self.to_list = [person_object.user.email,]

    def load_html_template(self):
        t = loader.get_template('inventory/email_certification_request.html')
        context ={
            'object': self.person_object,
            'queryset':  self.person_object.resource_people.filter(role=1)
        }
        rendered = t.render(context)
        return rendered

class FlagForDeletionEmail:

    def __init__(self, person_object):
        self.subject = 'A data resource has been flagged for deletion'
        self.message = self.load_html_template()
        self.from_email = from_email
        self.to_list = [admin_email,]

    def load_html_template(self):
        t = loader.get_template('inventory/email_flaged_for_deletion.html')
        context ={
            'object': object,
        }
        rendered = t.render(context)
        return rendered
