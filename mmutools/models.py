from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models
from lib.functions.custom_functions import nz
import os


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("english name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french name"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)


class GearType(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("english name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french name"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)


class Owner(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("english name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french name"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)


class Item(models.Model):
    item_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("name of item"))
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("description"))
    serial_number = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("serial number"))
    owner = models.ForeignKey(Owner, on_delete=models.DO_NOTHING, related_name="owners",
                              verbose_name=_("owner of equipment"))
    size = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("size (if applicable)"))
    container = models.BooleanField(default=False,
                                    verbose_name=_("is this item a container with more items inside it?"))
    container_space = models.IntegerField(null=True, blank=True,
                                          verbose_name=_("container Space Available (if applicable)"))
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name="categories",
                                 verbose_name=_("category of equipment"))
    gear_type = models.ForeignKey(GearType, on_delete=models.DO_NOTHING, related_name="types",
                                  verbose_name=_("type of equipment"))

    class Meta:
        unique_together = (('item_name', 'size'),)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("item_name"))):

            my_str = "{}".format(getattr(self, str(_("item_name"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = "{}".format(self.item_name)

        if self.size:
            my_str += f' ({self.size})'
        return my_str

    @property
    def tname(self):
        return str(self)

    def get_absolute_url(self):
        return reverse("mmutools:item_detail", kwargs={"pk": self.id})


class Lending(models.Model):
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name="lendings", verbose_name=_("item"))
    quantity_lent = models.IntegerField(null=True, blank=True, verbose_name=_("quantity lent"))
    lent_to = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("lent to"))
    lent_date = models.DateTimeField(blank=True, null=True, help_text="Format: YYYY-MM-DD HH:mm:ss",
                                     verbose_name=_("lent date"))
    return_date = models.DateTimeField(blank=True, null=True, help_text="Format: YYYY-MM-DD HH:mm:ss",
                                       verbose_name=_("expected return date"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("lent_to"))):

            return "{}".format(getattr(self, str(_("lent_to"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.lent_to)

    def get_absolute_url(self):
        return reverse("mmutools:lending_detail", kwargs={"pk": self.id})


class Quantity(models.Model):
    # choices for status
    ON_HAND = 'on hand'
    ON_ORDER = 'on order'
    LENT_OUT = 'lent out'
    STATUS_CHOICES = [
        (ON_HAND, _('On Hand')),
        (ON_ORDER, _('On Order')),
        (LENT_OUT, _('Lent Out')),
    ]
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name="quantities", verbose_name=_("item"))
    quantity = models.IntegerField(null=True, blank=True, verbose_name=_("quantity"))
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='ON_HAND', verbose_name=_("status"))
    lent_id = models.ForeignKey(Lending, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="lendee",
                                verbose_name=_("lent to"))
    last_audited = models.DateTimeField(blank=True, null=True, help_text="Format: YYYY-MM-DD HH:mm:ss",
                                        verbose_name=_("last audited"))
    last_audited_by = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("last audited by"))
    location_stored = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("location stored"))
    bin_id = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("bin id"))

    def __str__(self):

        # check to see if a french value is given
        if getattr(self, str(_("item"))):

            my_str = "{}".format(getattr(self, str(_("item"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = "{}".format(self.item)

        if self.quantity:
          return '{} - {}'.format(self.quantity, my_str) #TODO figure out why it doesn't like this in regular quantity add view

    def get_absolute_url(self):
        return reverse("mmutools:quantity_detail", kwargs={"pk": self.id})


class Supplier(models.Model):
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name="suppliers", verbose_name=_("item"))
    supplier = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("supplier"))
    contact_number = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("contact number"))
    email = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("email"))
    last_invoice = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("last invoice"))
    last_purchased = models.DateTimeField(blank=True, null=True, help_text="Format: YYYY-MM-DD HH:mm:ss",
                                          verbose_name=_("last purchased"))
    last_purchased_by = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("last purchased by"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("supplier"))):

            return "{}".format(getattr(self, str(_("supplier"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.supplier)

    def get_absolute_url(self):
        return reverse("mmutools:supplier_detail", kwargs={"pk": self.id})


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<item_name>_<size>/<filename>
    return 'mmutools/{0}_{1}/{2}'.format(instance.item.item_name, instance.item.size, filename)


class File(models.Model):
    caption = models.CharField(max_length=255, verbose_name=_("caption"))
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name="files", verbose_name=_("item"))
    file = models.FileField(upload_to=file_directory_path, verbose_name=_("file"))
    date_uploaded = models.DateTimeField(auto_now=True, editable=False, verbose_name=_("date uploaded"))

    class Meta:
        ordering = ['-date_uploaded']

    def __str__(self):
        return self.caption


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


class Organisation(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("english name"))
    abbrev_name = models.CharField(max_length=255, verbose_name=_("english abbreviated name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french name"))
    abbrev_nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french abbreviated name"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)


class Training(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)


class Experience(models.Model):
    EXPERIENCE_LEVEL_CHOICES = (
        ('None', _("No previous experience")),
        ('Novice', _("1-2 Necropsies")),
        ('Intermediate', _("3-5 Necropsies")),
        ('Advanced', _("More than 5 Necropsies")),
    )
    name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    nom = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    description_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("english description"))
    description_fra = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french description"))
    experience = models.CharField(max_length=255, choices=EXPERIENCE_LEVEL_CHOICES, default='None',
                                  verbose_name=_("experience level"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    def get_absolute_url(self):
        return reverse("mmutools:personnel_detail", kwargs={"pk": self.id})


class Personnel(models.Model):
    first_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("first name"))
    last_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("last name"))
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name="people",
                                     verbose_name=_("organisation"), null=True, blank=True)
    email = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("email address"))
    phone = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("phone number"))
    exp_level = models.ForeignKey(Experience, help_text="Novice 1-2 necropsy, Intermediate 3-5, Advanced more than 5",
                                  on_delete=models.DO_NOTHING, related_name="xp",
                                  verbose_name=_("experience level"))
    training = models.ManyToManyField(Training, verbose_name=_("training"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("first_name"))):

            return "{}".format(getattr(self, str(_("first_name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.first_name)

    def get_absolute_url(self):
        return reverse("mmutools:personnel_detail", kwargs={"pk": self.id})


BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))

REGION_CHOICES = (
    ("Gulf", "Gulf"),
    ("Mar", "Maritimes"),
    ("NL", "Newfoundland"),
    ("QC", "Quebec"),
)

SEX_CHOICES = (
    ("M", "Male"),
    ("F", "Female"),
    ("UnK", "Unknown"),
)

AGE_CHOICES = (
    ("J", "Juvenile"),
    ("YA", "Young Adult"),
    ("A", "Adult"),
)

INCIDENT_CHOICES = (
    ("E", "Entangled"),
    ("DF", "DEAD - Floating"),
    ("DB", "DEAD - Beached"),
    ("N", "Necropsy"),
)


class Incident(models.Model):
    species_count = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("species count"))
    submitted = models.BooleanField(choices=BOOL_CHOICES, blank=True, null=True,
                                    verbose_name=_("incident report submitted by Gulf?"))
    first_report = models.DateTimeField(blank=True, null=True, help_text="Format: YYYY-MM-DD HH:mm:ss",
                                        verbose_name=_("date and time first reported"))
    lat = models.FloatField(blank=True, null=True, verbose_name=_("latitude (DD)"))
    long = models.FloatField(blank=True, null=True, verbose_name=_("longitude (DD)"))
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("location"))
    region = models.CharField(max_length=255, null=True, blank=True, choices=REGION_CHOICES, verbose_name=_("region"))
    species = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("species"))
    sex = models.CharField(max_length=255, blank=True, null=True, choices=SEX_CHOICES, verbose_name=_("sex"))
    age_group = models.CharField(max_length=255, blank=True, null=True, choices=AGE_CHOICES,
                                 verbose_name=_("age group"))
    incident_type = models.CharField(max_length=255, blank=True, null=True, choices=INCIDENT_CHOICES,
                                     verbose_name=_("type of Incident"))
    gear_presence = models.BooleanField(blank=True, null=True, choices=BOOL_CHOICES, verbose_name=_("gear Presence?"))
    gear_desc = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("gear description"))
    exam = models.BooleanField(blank=True, null=True, choices=BOOL_CHOICES, verbose_name=_("examination conducted?"))
    necropsy = models.BooleanField(blank=True, null=True, choices=BOOL_CHOICES, verbose_name=_("necropsy conducted?"))
    results = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("results"))
    photos = models.BooleanField(blank=True, null=True, choices=BOOL_CHOICES, verbose_name=_("photos?"))
    data_folder = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("data folder"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("comments/Details"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("species_count"))):

            return "{}".format(getattr(self, str(_("species_count"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.species_count)

    def get_absolute_url(self):
        return reverse("mmutools:incident_detail", kwargs={"pk": self.id})
