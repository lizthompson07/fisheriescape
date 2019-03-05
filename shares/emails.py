from django.template import loader

from_email = 'DoNotReply@DFOScienceDataManagement.com'
admin_email = 'david.fishman@dfo-mpo.gc.ca'


class SendInstructionsEmail:
    def __init__(self, object):
        self.subject = 'Your NAS user account has been created'
        self.message = self.load_html_template(object)
        self.from_email = from_email
        self.to_list = [admin_email, object.user.email]

    def load_html_template(self, object):
        t = loader.get_template('shares/email_instructions.html')
        context = {'object': object}
        rendered = t.render(context)
        return rendered
