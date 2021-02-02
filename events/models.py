from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext

from masterlist.models import Person
from shared_models.models import SimpleLookup, Lookup, HelpTextLookup, FiscalYear
from shared_models.utils import get_metadata_string


class Event(SimpleLookup):
    type_choices = (
        (1, _("CSAS meeting")),
        (9, _("other")),
    )

    # basic
    location = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("location"))
    proponent = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("proponent"))
    type = models.IntegerField(choices=type_choices, verbose_name=_("type of event"))
    start_date = models.DateTimeField(verbose_name=_("initial activity date"), blank=True, null=True)
    end_date = models.DateTimeField(verbose_name=_("anticipated end date"), blank=True, null=True)

    # calculated
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("fiscal year"), related_name="events",
                                    editable=False)
    # meta
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("date last modified"), editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, verbose_name=_("last modified by"), editable=False, related_name="user_events_updated_by")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("date created"), editable=False)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, verbose_name=_("created by"), related_name="user_events_created_by", editable=False)

    @property
    def metadata(self):
        return get_metadata_string(
            self.created_at,
            self.created_by,
            self.updated_at,
            self.updated_by,
        )

    class Meta:
        ordering = ['-updated_at', ]



class Invitee(models.Model):
    # Choices for role
    role_choices = (
        (1, 'attendee'),
        (2, 'chair'),
        (3, 'expert'),
    )
    status_choices = (
        (1, 'invited'),
        (2, 'accepted'),
        (3, 'declined'),
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="invitees")
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, verbose_name=_("person"), related_name="invitees")
    role = models.IntegerField(choices=role_choices, verbose_name=_("role"), default=1)
    organization = models.CharField(max_length=50)
    status = models.IntegerField(choices=status_choices, verbose_name=_("status"), default=1)
    invitation_sent_date = models.DateTimeField(verbose_name=_("date invitation was sent"), editable=False, blank=True, null=True)
    resources_received = models.ManyToManyField("Resource", editable=False)


    class Meta:
        ordering = ['status', 'role', 'person__first_name', "person__last_name"]


class Note(models.Model):
    # Choices for type
    type_choices = (
        (1, 'To Do'),
        (2, 'Next step'),
        (3, 'General comment'),
    )

    event = models.ForeignKey(Event, related_name='notes', on_delete=models.CASCADE)
    type = models.IntegerField(choices=type_choices, verbose_name=_("type"))
    note = models.TextField(verbose_name=_("note"))
    is_complete = models.BooleanField(default=False, verbose_name=_("complete?"))

    # meta
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("date last modified"), editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, verbose_name=_("last modified by"), editable=False, related_name="user_event_notes_updated_by")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("date created"), editable=False)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, verbose_name=_("created by"), editable=False, related_name="user_event_notes_created_by")

    @property
    def metadata(self):
        return get_metadata_string(
            self.created_at,
            self.created_by,
            self.updated_at,
            self.updated_by,
        )

    class Meta:
        ordering = ["-updated_at"]


def resource_directory_path(instance, filename):
    return 'events/{0}/{1}'.format(instance.event.id, filename)


class Resource(SimpleLookup):
    url_en = models.URLField(verbose_name=_("url (English)"), blank=True, null=True)
    url_fr = models.URLField(verbose_name=_("url (French)"), blank=True, null=True)
    file_en = models.FileField(upload_to=resource_directory_path, verbose_name=_("file attachment (English)"), blank=True, null=True)
    file_fr = models.FileField(upload_to=resource_directory_path, verbose_name=_("file attachment (French)"), blank=True, null=True)

    # meta
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("date last modified"), editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, verbose_name=_("last modified by"), editable=False, related_name="user_event_resources_updated_by")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("date created"), editable=False)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, verbose_name=_("created by"), related_name="user_event_resources_created_by",
                                   editable=False)

    @property
    def metadata(self):
        return get_metadata_string(
            self.created_at,
            self.created_by,
            self.updated_at,
            self.updated_by,
        )

    @property
    def tfile(self):
        # check to see if a french value is given
        if getattr(self, gettext("file_en")):
            return getattr(self, gettext("file_en"))
        # if there is no translated term, just pull from the english field
        else:
            return self.file_en

    @property
    def turl(self):
        # check to see if a french value is given
        if getattr(self, gettext("url_en")):
            return getattr(self, gettext("url_en"))
        # if there is no translated term, just pull from the english field
        else:
            return self.url_en

    class Meta:
        ordering = [_("name")]


