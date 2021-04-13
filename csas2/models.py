from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import date
from django.utils.translation import gettext_lazy as _, gettext

from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, FiscalYear, Region, MetadataFields, Language


class Person(models.Model):
    # Choices for role
    first_name = models.CharField(max_length=100, verbose_name=_("first name"))
    last_name = models.CharField(max_length=100, verbose_name=_("last name"), blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("phone"))
    email = models.EmailField(verbose_name=_("email"), unique=True)
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("language preference"))
    organization = models.CharField(max_length=50, verbose_name=_("association"), blank=True, null=True)
    dmapps_user = models.ForeignKey(User, blank=True, null=True, verbose_name=_("linkage to DM Apps User"))

    class Meta:
        ordering = ['first_name', "last_name"]

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)


class Process(SimpleLookup, MetadataFields):
    pass


class Meeting(SimpleLookup, MetadataFields):
    type_choices = (
        (1, _("CSAS Regional Advisory Process (RAP)")),
        (2, _("CSAS Science Management Meeting")),
        (3, _("CSAS Steering Committee Meeting")),
        (9, _("other")),
    )

    process = models.ForeignKey(Process, related_name='meetings', on_delete=models.CASCADE, verbose_name=_("process"), editable=False)
    # basic
    location = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("location"))
    proponent = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("proponent"))
    type = models.IntegerField(choices=type_choices, verbose_name=_("type of event"))
    start_date = models.DateTimeField(verbose_name=_("initial activity date"), blank=True, null=True)
    end_date = models.DateTimeField(verbose_name=_("anticipated end date"), blank=True, null=True)
    from_email = models.EmailField(default=settings.SITE_FROM_EMAIL, verbose_name=_("FROM email address (on invitation)"))
    rsvp_email = models.EmailField(verbose_name=_("RSVP email address (on invitation)"))

    # calculated
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("fiscal year"), related_name="events",
                                    editable=False)

    class Meta:
        ordering = ['-updated_at', ]

    @property
    def attendees(self):
        return Attendance.objects.filter(invitee__event=self).order_by("invitee").values("invitee").distinct()

    @property
    def length_days(self):
        if self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 1

    @property
    def display_dates(self):
        start = date(self.start_date) if self.start_date else "??"
        dates = f'{start}'
        if self.end_date and self.end_date != self.start_date:
            end = date(self.end_date)
            dates += f' &rarr; {end}'
        days_display = "{} {}{}".format(self.length_days, gettext("day"), pluralize(self.length_days))
        dates += f' ({days_display})'
        return dates


class Invitee(models.Model):
    # Choices for role
    role_choices = (
        (1, 'Participant'),
        (2, 'Chair'),
        (3, 'Expert'),
        (4, 'Steering Committee Member'),
    )
    status_choices = (
        (0, 'Invited'),
        (1, 'Accepted'),
        (2, 'Declined'),
        (9, 'No response'),
    )
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="invitees")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="meeting_invites")
    role = models.IntegerField(choices=role_choices, verbose_name=_("Function"), default=1)
    status = models.IntegerField(choices=status_choices, verbose_name=_("status"), default=0)
    invitation_sent_date = models.DateTimeField(verbose_name=_("date invitation was sent"), editable=False, blank=True, null=True)
    resources_received = models.ManyToManyField("Resource", editable=False)

    class Meta:
        ordering = ['first_name', "last_name"]
        unique_together = (("event", "email"),)

    @property
    def attendance_fraction(self):
        return self.attendance.count() / self.meeting.length_days


class Attendance(models.Model):
    invitee = models.ForeignKey(Invitee, on_delete=models.CASCADE, related_name="attendance", verbose_name=_("attendee"))
    date = models.DateTimeField(verbose_name=_("date"))

    class Meta:
        ordering = ['date']
        unique_together = (("invitee", "date"),)


class MeetingNote(MetadataFields):
    # Choices for type
    type_choices = (
        (1, 'To Do'),
        (2, 'Next step'),
        (3, 'General comment'),
    )

    meeting = models.ForeignKey(Meeting, related_name='notes', on_delete=models.CASCADE)
    type = models.IntegerField(choices=type_choices, verbose_name=_("type"))
    note = models.TextField(verbose_name=_("note"))
    is_complete = models.BooleanField(default=False, verbose_name=_("complete?"))

    class Meta:
        ordering = ["is_complete", "-updated_at", ]


def resource_directory_path(instance, filename):
    return 'events/{0}/{1}'.format(instance.event.id, filename)


class MeetingResource(SimpleLookup, MetadataFields):
    event = models.ForeignKey(Meeting, related_name='resources', on_delete=models.CASCADE)

    url_en = models.URLField(verbose_name=_("url (English)"), blank=True, null=True)
    url_fr = models.URLField(verbose_name=_("url (French)"), blank=True, null=True)

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
