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

class SectionReportEmail:

    def __init__(self, person_object, section):
        self.person_object = person_object
        self.section = section
        self.queryset = section.resources.all().order_by("title_eng")
        self.subject = "Your Section's Data Inventory"
        self.message = self.load_html_template()
        self.from_email = admin_email
        self.to_list = [person_object.user.email,]

    def load_html_template(self):
        t = loader.get_template('inventory/email_section_head_report.html')
        context ={
            'object': self.person_object,
            'queryset':  self.queryset,
            'section':  self.section,
        }
        rendered = t.render(context)
        return rendered

class FlagForDeletionEmail:

    def __init__(self, object, user):
        self.subject = 'A data resource has been flagged for deletion'
        self.message = self.load_html_template(object,user)
        self.from_email = from_email
        self.to_list = [admin_email,]

    def load_html_template(self, object,user):
        t = loader.get_template('inventory/email_flagged_for_deletion.html')
        context ={
            'object': object,
            'user': user,
        }
        rendered = t.render(context)
        return rendered


class FlagForPublicationEmail:

    def __init__(self, object, user):
        self.subject = 'A data resource has been flagged for publication'
        self.message = self.load_html_template(object,user)
        self.from_email = from_email
        self.to_list = [admin_email,]

    def load_html_template(self, object,user):
        t = loader.get_template('inventory/email_flagged_for_publication.html')
        context ={
            'object': object,
            'user': user,
        }
        rendered = t.render(context)
        return rendered

class AddedAsCustodianEmail:

    def __init__(self, object, user):
        self.subject = 'You have been added as a custodian'
        self.message = self.load_html_template(object,user)
        self.from_email = from_email
        self.to_list = [user.email,]

    def load_html_template(self, object,user):
        t = loader.get_template('inventory/email_added_as_custodian.html')
        context ={
            'object': object,
            'user': user,
        }
        rendered = t.render(context)
        return rendered
