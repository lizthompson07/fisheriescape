from django.template import loader
from . import models

from_email='DoNotReply@RDMTS.com'
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
