from django.conf import settings
from django.template import loader

from dm_apps.context_processor import my_envr

from_email = settings.SITE_FROM_EMAIL


class UserCreationEmail:
    def __init__(self, user_object, request):
        self.request = request
        self.subject = "DM Apps account creation / Création de compte d'Application GD"
        self.message = self.load_html_template(object)
        self.from_email = from_email
        self.to_list = []

        try:
            self.to_list.append(user_object.email)
        except AttributeError:
            self.to_list.append("david.fishman@dfo-mpo.gc.ca")

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, user_object):
        t = loader.get_template('shared_models/email_user_creation.html')
        context = {'object': user_object, "created_by": self.request.user}
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered
