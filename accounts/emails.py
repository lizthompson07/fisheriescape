from django.template import loader
from django.conf import settings

app_name = settings.WEB_APP_NAME # should be a single word with one space
from_email='DoNotReply@{}.com'.format(app_name)
admin_email = 'david.fishman@dfo-mpo.gc.ca'

class AccountRequestEmail:

    def __init__(self, object):
        self.subject = 'grAIS: A new account is being requested'
        self.message = self.load_html_template(object)
        self.from_email = from_email
        self.to_list = [admin_email,]

    def load_html_template(self,object):
        t = loader.get_template('registration/email_account_request.html')
        context ={ 'object': object }
        rendered = t.render(context)
        return rendered
