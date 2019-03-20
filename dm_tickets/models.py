import os
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
# from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
import markdown

from lib.functions.fiscal_year import fiscal_year
from shared_models import models as shared_models


# Create your models here.

class Person(models.Model):
    first_name = models.CharField(max_length=225)
    last_name = models.CharField(max_length=225, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    class Meta:
        ordering = ['first_name', 'last_name']

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('tickets:person_detail', kwargs={'pk': self.id})


class RequestType(models.Model):
    request_type = models.CharField(max_length=255)
    financial_follow_up_needed = models.BooleanField(default=False)

    def __str__(self):
        return self.request_type

    class Meta:
        ordering = ['request_type', ]


class Tag(models.Model):
    tag = models.CharField(max_length=255)

    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        return reverse('tickets:tag_detail', kwargs={'pk': self.id})

    class Meta:
        ordering = ['tag']


class Ticket(models.Model):
    # Choices for status
    RESOLVED = '2'
    ACTIVE = '5'
    IDLE = '6'
    CANCELLED = '7'
    WISHLIST = '8'
    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (RESOLVED, 'Resolved'),
        (IDLE, 'Idle'),
        (CANCELLED, 'Cancelled'),
        (WISHLIST, 'Wishlist'),
    )

    # Choices for priority
    HIGH = '1'
    MED = '2'
    LOW = '3'
    WISHLIST = '4'
    URGENT = '5'
    PRIORITY_CHOICES = (
        (HIGH, 'High'),
        (MED, 'Medium'),
        (LOW, 'Low'),
        (WISHLIST, 'Wish List'),
        (URGENT, 'Urgent'),
    )

    title = models.CharField(max_length=255)
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING)
    status = models.CharField(default=ACTIVE, max_length=1, choices=STATUS_CHOICES)
    priority = models.CharField(default=HIGH, max_length=1, choices=PRIORITY_CHOICES)
    request_type = models.ForeignKey(RequestType, on_delete=models.DO_NOTHING)
    description = models.TextField(blank=True, null=True)
    financial_coding = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    notes_html = models.TextField(blank=True, null=True, verbose_name="Notes")
    date_opened = models.DateTimeField(default=timezone.now)
    date_closed = models.DateTimeField(null=True, blank=True)
    date_modified = models.DateTimeField(default=timezone.now)
    people = models.ManyToManyField(Person, related_name='tickets')
    tags = models.ManyToManyField(Tag)
    primary_contact = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
    resolved_email_date = models.DateTimeField(null=True, blank=True,
                                               verbose_name="Notification sent to primary contact")
    # SERVICE DESK FIELDS
    sd_ref_number = models.CharField(max_length=8, null=True, blank=True, verbose_name="Service desk reference #")
    sd_ticket_url = models.URLField(null=True, blank=True, verbose_name="Service desk ticket URL")
    sd_primary_contact = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name="sd_tickets_persons",
                                           null=True, blank=True, verbose_name="Service desk primary contact")
    sd_description = models.TextField(null=True, blank=True, verbose_name="Service desk ticket description")
    sd_date_logged = models.DateTimeField(null=True, blank=True, verbose_name="Service desk date logged")
    financial_follow_up_needed = models.BooleanField(default=False)
    estimated_cost = models.FloatField(blank=True, null=True)
    # fiscal_year = models.CharField(blank=True, null=True, max_length=20) # THIS FIELD SHOULD BE DELETED
    fiscal_year = models.ForeignKey(shared_models.FiscalYear, blank=True, null=True, on_delete=models.DO_NOTHING)

    def save(self, *args, **kwargs):
        if self.notes:
            self.notes_html = markdown.markdown(self.notes)

        self.date_modified = timezone.now()

        # if status is resolved or canceled, add a date closed timestamp
        if self.status is '2' or self.status is '7':
            self.date_closed = timezone.now()
        else:
            self.date_closed = None

        self.fiscal_year_id = fiscal_year(self.date_opened.year, sap_style=True)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_modified']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tickets:detail', kwargs={'pk': self.id})

    @property
    def search_clob(self):
        return "{} {} {} {} {} {}".format(self.title, self.description, self.service_desk_ticket, self.request_type,
                                          self.people.all(), self.tags.all())

    @property
    def tags_pretty(self):
        my_str = ""
        for tag in self.tags.all():
            my_str = my_str + tag.tag + ", "

        return my_str[:len(my_str) - 2]

    @property
    def people_pretty(self):
        my_str = ""
        for person in self.people.all():
            my_str = my_str + "{} {},<br>".format(person.first_name, person.last_name)

        return my_str[:len(my_str) - 5]


def ticket_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'dm_tickets/ticket_{0}/{1}'.format(instance.ticket.id, filename)


class File(models.Model):
    caption = models.CharField(max_length=255)
    ticket = models.ForeignKey(Ticket, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to=ticket_directory_path, null=True, blank=True)
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.caption

    def get_absolute_url(self):
        return reverse('tickets:file_detail', kwargs={
            'ticket': self.ticket.id,
            'pk': self.id
        })


@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = File.objects.get(pk=instance.pk).file
    except File.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
