from django.conf import settings
from django.contrib.auth.models import User
from django.template import loader

from dm_apps.context_processor import my_envr
from dm_apps.emails import Email
from . import models

app_name = settings.WEB_APP_NAME  # should be a single word with one space
from_email = settings.SITE_FROM_EMAIL


class CertificationRequestEmail(Email):
    email_template_path = 'inventory/emails/email_certification_request.html'
    subject_en = 'Your metadata records (*** ACTION REQUIRED ***)'

    def get_recipient_list(self):
        return [self.instance.email, self.request.user.email]

    def get_context_data(self):
        context = super().get_context_data()
        context["records"] = models.Resource.objects.filter(resource_people2__user=self.instance, resource_people2__roles__code__iexact="RI_409").distinct()
        return context


class FlagForDeletionEmail(Email):
    email_template_path = 'inventory/emails/email_flagged_for_deletion.html'
    subject_en = 'A data resource has been flagged for deletion'

    def get_recipient_list(self):
        return [user.email for user in User.objects.filter(inventory_user__isnull=False).distinct()]

    def __init__(self, request, instance=None, user=None):
        super().__init__(request)
        self.request = request
        self.instance = instance
        self.user = user

    def get_context_data(self):
        context = super().get_context_data()
        context["user"] = self.user
        return context


class FlagForPublicationEmail(Email):
    email_template_path = 'inventory/emails/email_flagged_for_publication.html'
    subject_en = 'A data resource has been flagged for publication'

    def get_recipient_list(self):
        return [user.email for user in User.objects.filter(inventory_user__isnull=False).distinct()]

    def __init__(self, request, instance=None, user=None):
        super().__init__(request)
        self.request = request
        self.instance = instance
        self.user = user

    def get_context_data(self):
        context = super().get_context_data()
        context["user"] = self.user
        return context


class AddedAsCustodianEmail(Email):
    email_template_path = 'inventory/emails/email_added_as_custodian.html'
    subject_en = 'You have been added as a custodian'

    def get_recipient_list(self):
        return [self.user.email]

    def __init__(self, request, instance=None, user=None):
        super().__init__(request)
        self.request = request
        self.instance = instance
        self.user = user

    def get_context_data(self):
        context = super().get_context_data()
        context["user"] = self.user
        return context


class RemovedAsCustodianEmail(Email):
    email_template_path = 'inventory/emails/email_removed_as_custodian.html'
    subject_en = 'You have been removed as a custodian'

    def get_recipient_list(self):
        return [self.user.email]

    def __init__(self, request, instance=None, user=None):
        super().__init__(request)
        self.request = request
        self.instance = instance
        self.user = user

    def get_context_data(self):
        context = super().get_context_data()
        context["user"] = self.user
        return context

