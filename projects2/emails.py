from django.conf import settings
from django.template import loader

from dm_apps.context_processor import my_envr

from_email = settings.SITE_FROM_EMAIL


class StaffEmail:
    def __init__(self, staff, action, request):
        self.request = request
        if action == "add":
            self.subject = 'You have been added to a project / Vous avez été ajouté à un projet'
        else:
            self.subject = "You have been removed from a project / Vous avez été retiré d'un projet"

        self.message = self.load_html_template(staff, action)
        self.from_email = from_email
        try:
            self.to_list = [staff.user.email]
        except AttributeError:
            self.to_list = []

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, staff, action):
        t = loader.get_template('projects2/emails/staff_change.html')
        context = {'staff': staff, "action": action}
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered

class ProjectReviewEmail:
    def __init__(self, review, request):
        self.request = request
        self.subject = 'Your project has been reviewed / Votre projet a été examiné'
        self.message = self.load_html_template(review)
        self.from_email = from_email
        self.to_list = [u.email for u in review.project_year.get_project_leads_as_users()]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, review):
        t = loader.get_template('projects2/emails/project_reviewed.html')
        context = {'review': review, }
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered


class ProjectApprovalEmail:
    def __init__(self, review, request):
        self.request = request
        if review.approval_status == 1:
            self.subject = 'Your project has been approved / Votre projet a été approuvé'
        elif review.approval_status == 0:
            self.subject = "Your project has not been approved / Votre projet n'a pas été approuvé"
        else:
            self.subject = "Your project status has been updated / Le statut de votre projet a été mis à jour"
        self.message = self.load_html_template(review)
        self.from_email = from_email
        self.to_list = [u.email for u in review.project_year.get_project_leads_as_users()]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, review):
        t = loader.get_template('projects2/emails/email_project_approved.html')
        context = {'object': review, }
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered


class ProjectYearSubmissionEmail:
    def __init__(self, object, request):
        self.request = request
        if object.submitted:
            self.subject = 'A project has been submitted under your section / Un projet a été soumis dans votre section'
        else:
            self.subject = 'A project has been unsubmitted from your section / Un projet a été annulé dans votre section'

        self.message = self.load_html_template(object)
        self.from_email = from_email
        try:
            self.to_list = [object.project.section.head.email]
        except AttributeError:
            self.to_list = ["david.fishman@dfo-mpo.gc.ca"]

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, object):
        t = loader.get_template('projects2/emails/email_project_submitted.html')
        context = {'object': object}
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered


class UserCreationEmail:
    def __init__(self, object, request):
        self.request = request
        self.subject = 'DM Apps account creation / Création de compte DM Apps'
        self.message = self.load_html_template(object)
        self.from_email = from_email
        self.to_list = []

        try:
            self.to_list.append(object.email)
        except AttributeError:
            self.to_list.append("david.fishman@dfo-mpo.gc.ca")

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)

    def load_html_template(self, object):
        t = loader.get_template('projects/email_user_creation.html')
        context = {'object': object, }
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered
