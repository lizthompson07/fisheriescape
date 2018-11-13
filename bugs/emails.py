from django.conf import settings
from django.template import loader
from . import models

admin_email = 'david.fishman@dfo-mpo.gc.ca'
app_name = settings.WEB_APP_NAME # should be a single word with one space
from_email='DoNotReply@{}.com'.format(app_name)

class NewBugNotificationEmail:

    def __init__(self, object, application):
        self.subject = '{}: A new bug has been logged'.format(app_name)
        self.message = self.load_html_template(object,application)
        self.from_email = from_email
        self.to_list = [admin_email,]

    def load_html_template(self,object, application):
        t = loader.get_template('bugs/email_new_bug_notification.html')
        context = {
            'object': object,
            'app_name': models.Bug.APP_DICT[application]
        }
        rendered = t.render(context)
        return rendered
