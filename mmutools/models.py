from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models
from lib.functions.custom_functions import nz

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("English name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("French name"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

class GearType(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("English name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("French name"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)


class Owner(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("English name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("French name"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

class Item(models.Model):
    item_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Name of Item"))
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Description"))
    serial_number = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Serial Number"))
    owner = models.ForeignKey(Owner, on_delete=models.DO_NOTHING, related_name="owner",
                                                  verbose_name=_("Owner of Equipment"))
    size = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Size (if applicable)"))
    container = models.BooleanField(default=False, verbose_name=_("Is this item a container with more items inside it?"))
    container_space = models.IntegerField(null=True, blank=True,
                                          verbose_name=_("Container Space Available (if applicable)"))
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name="category",
                                                  verbose_name=_("Category of Equipment"))
    gear_type = models.ForeignKey(GearType, on_delete=models.DO_NOTHING, related_name="type",
                                                  verbose_name=_("Type of Equipment"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("item_name"))):

            return "{}".format(getattr(self, str(_("item_name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.item_name)

    def get_absolute_url(self):
        return reverse("mmutools:item_detail", kwargs={"pk": self.id})

class Lending(models.Model):
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name="necropsy_lending_related", related_query_name="necropsy_lendings",
                                           verbose_name=_("Item"))
    quantity_lent = models.IntegerField(null=True, blank=True, verbose_name=_("Quantity Lent"))
    lent_to = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Lent To"))
    lent_date = models.DateTimeField(blank=True, null=True, help_text="Format: YYYY-MM-DD HH:mm:ss", verbose_name=_("Lent Date"))

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
    #choices for status
    ON_HAND = 'on hand'
    ON_ORDER = 'on order'
    LENT_OUT = 'lent out'
    STATUS_CHOICES = [
        (ON_HAND, _('On Hand')),
        (ON_ORDER, _('On Order')),
        (LENT_OUT, _('Lent Out')),
    ]
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name="necropsy_quantity_related", related_query_name="necropsy_quantitys",
                                      verbose_name=_("Item"))
    quantity = models.IntegerField(null=True, blank=True, verbose_name=_("Quantity"))
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='ON_HAND', verbose_name=_("Status"))
    lent_id = models.ForeignKey(Lending, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="lendee",
                                           verbose_name=_("Lent To"))
    last_audited = models.DateTimeField(blank=True, null=True, help_text="Format: YYYY-MM-DD HH:mm:ss", verbose_name=_("Last Audited"))
    last_audited_by = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Last Audited By"))
    location_stored = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Location Stored"))
    bin_id = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Bin Id"))

    def __str__(self):

        # check to see if a french value is given
        if getattr(self, str(_("id"))):

            return "{}".format(getattr(self, str(_("id"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.id)

    def get_absolute_url(self):
        return reverse("mmutools:quantity_detail", kwargs={"pk": self.id})

    # @property
    # def quantity_avail(self):
    #
    #     Myobj = Quantity.objects.filter(status='on hand').aggregate(dsum=Sum('quantity'))
    #     Myobj2 = Quantity.objects.filter(status='lent out').aggregate(dsum=Sum('quantity'))
    #
    #     return Myobj["dsum"]-Myobj2["dsum"]


class Supplier(models.Model):
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name="necropsy_supplier_related", related_query_name="necropsy_suppliers",
                             verbose_name=_("Item"))
    supplier = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Supplier"))
    contact_number = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Contact Number"))
    email = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Email"))
    last_invoice = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Last Invoice"))
    last_purchased = models.DateTimeField(blank=True, null=True, help_text="Format: YYYY-MM-DD HH:mm:ss", verbose_name=_("Last Purchased"))
    last_purchased_by = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Last Purchased by"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("supplier"))):

            return "{}".format(getattr(self, str(_("supplier"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.supplier)

    def get_absolute_url(self):
        return reverse("mmutools:supplier_detail", kwargs={"pk": self.pk})


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/supplier_<id>/<filename>
    return 'mmutools/supplier_{0}/{1}'.format(instance.supplier.id, filename)

class File(models.Model):
    caption = models.CharField(max_length=255, verbose_name=_("caption"))
    supplier = models.ForeignKey(Supplier, on_delete=models.DO_NOTHING, related_name="necropsy_file_related",
                                 related_query_name="necropsy_files", verbose_name=_("Supplier"))
    file = models.FileField(upload_to=file_directory_path, verbose_name=_("file"))
    date_uploaded = models.DateTimeField(default=timezone.now, verbose_name=_("date uploaded"))

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
    name = models.CharField(max_length=255, verbose_name=_("English name"))
    abbrev_name = models.CharField(max_length=255, verbose_name=_("English abbreviated name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("French name"))
    abbrev_nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("French abbreviated name"))

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
    description_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("English description"))
    description_fra = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("French description"))
    experience = models.CharField(max_length=255, choices=EXPERIENCE_LEVEL_CHOICES, default='None', verbose_name=_("Experience level"))

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
    first_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("First name"))
    last_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Last name"))
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name="people", verbose_name=_("Organisation"), null=True, blank=True)
    email = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Email address"))
    phone = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Phone number"))
    exp_level = models.ForeignKey(Experience, help_text="Novice 1-2 necropsy, Intermediate 3-5, Advanced more than 5", on_delete=models.DO_NOTHING, related_name="xp",
                                                  verbose_name=_("Experience level"))
    training = models.ManyToManyField(Training, verbose_name=_("Training"))

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
    species_count = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Species count"))
    submitted = models.BooleanField(choices=BOOL_CHOICES, blank=True, null=True, verbose_name=_("Incident report submitted by Gulf?"))
    first_report = models.DateTimeField(blank=True, null=True, help_text="Format: YYYY-MM-DD HH:mm:ss", verbose_name=_("Date and time first reported"))
    lat = models.FloatField(blank=True, null=True, verbose_name=_("Latitude (DD)"))
    long = models.FloatField(blank=True, null=True, verbose_name=_("Longitude (DD)"))
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Location"))
    region = models.CharField(max_length=255, null=True, blank=True, choices=REGION_CHOICES, verbose_name=_("Region"))
    species = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Species"))
    sex = models.CharField(max_length=255, blank=True, null=True, choices=SEX_CHOICES, verbose_name=_("Sex"))
    age_group = models.CharField(max_length=255, blank=True, null=True, choices=AGE_CHOICES, verbose_name=_("Age group"))
    incident_type = models.CharField(max_length=255, blank=True, null=True, choices=INCIDENT_CHOICES, verbose_name=_("Type of Incident"))
    gear_presence = models.BooleanField(blank=True, null=True, choices=BOOL_CHOICES, verbose_name=_("Gear Presence?"))
    gear_desc = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("Gear description"))
    exam = models.BooleanField(blank=True, null=True, choices=BOOL_CHOICES, verbose_name=_("Examination conducted?"))
    necropsy = models.BooleanField(blank=True, null=True, choices=BOOL_CHOICES, verbose_name=_("Necropsy conducted?"))
    results = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("Results"))
    photos = models.BooleanField(blank=True, null=True, choices=BOOL_CHOICES, verbose_name=_("Photos?"))
    data_folder = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Data folder"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("Comments/Details"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("species_count"))):

            return "{}".format(getattr(self, str(_("species_count"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.species_count)

    def get_absolute_url(self):
        return reverse("mmutools:incident_detail", kwargs={"pk": self.id})