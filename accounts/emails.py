from django.template import loader

from_email='DoNotReply@RDMTS.com'
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
