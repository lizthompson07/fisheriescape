from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

from phonenumber_field.modelfields import PhoneNumberField

from shared_models.models import Province

ORGANIZATION_TYPES = [
    ('', '----'),
    ('Federal Government', 'Federal Government'),
    ('Provincial/State Government', 'Provincial/State Government'),
    ('Municipal Government', 'Municipal Government'),
    ('Indigenous Group/Government', 'Indigenous Group/Government'),
    ('Association', 'Association'),
    ('Small and Medium-Sized Business', 'Small and Medium-Sized Business'),
    ('Multinational Enterprise', 'Multinational Enterprise'),
    ('Accelerator/Incubator/Network', 'Accelerator/Incubator/Network'),
    ('PSI', 'Post-Secondary Institution'),
    ('Other', 'Other')
]

PROFIT_OPTIONS = [
    (None, '----'),
    (1, 'Profit'),
    (0, 'Non-Profit')
]

STAKEHOLDER_TYPE = [
    (1, 'Internal'),
    (2, 'Government of Canada'),
    (3, 'External')
]


class Organization(models.Model):
    legal_name = models.CharField(max_length=127)
    phone_number = PhoneNumberField(blank=True)
    fax_number = PhoneNumberField(blank=True)
    email = models.EmailField(blank=True)
    webpage = models.URLField(blank=True)
    business_number = models.CharField('CRA Business Number', max_length=12, blank=True)
    address_line_1 = models.CharField(max_length=31, blank=True)
    address_line_2 = models.CharField(max_length=31, blank=True)
    city = models.CharField(max_length=15, blank=True)
    province = models.ForeignKey(Province, on_delete=models.DO_NOTHING, blank=True, related_name='organizations',
                                 null=True)
    zip_postal = models.CharField("ZIP/Postal Code", max_length=10, blank=True)
    country = models.CharField(max_length=50, blank=True, default='Canada')
    organization_type = models.CharField(max_length=50, choices=ORGANIZATION_TYPES, default='', blank=True)
    other_organization_type = models.CharField(max_length=50, blank=True)  # Show if organization_type == 'Other'
    profit_nonprofit = models.PositiveIntegerField('Profit/Non-Profit', choices=PROFIT_OPTIONS, default=None,
                                                   blank=True, null=True)
    stakeholder_type = models.PositiveIntegerField(choices=STAKEHOLDER_TYPE, default=3)
    parent_organizations = models.ManyToManyField('self', blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_organizations')
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='modified_organizations')
    slug = models.SlugField(max_length=127)

    def __str__(self):
        return self.legal_name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.__str__())
        super(Organization, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('organizations_detail', kwargs={'slug': self.slug})

class Individual(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    title = models.CharField(max_length=45, blank=True)
    organization = models.ManyToManyField(Organization, blank=True)
    email_address = models.EmailField(blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    fax_number = PhoneNumberField(blank=True, null=True)
    address_line_1 = models.CharField(max_length=31, blank=True)
    address_line_2 = models.CharField(max_length=31, blank=True)
    city = models.CharField(max_length=15, blank=True)
    province = models.ForeignKey(Province, on_delete=models.DO_NOTHING, blank=True, related_name='individuals', null=True)
    zip_postal = models.CharField("ZIP/Postal Code", max_length=10, blank=True)
    country = models.CharField(max_length=50, blank=True, default='Canada')
    linkedin_profile = models.URLField("LinkedIn profile", blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    last_modified = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=127)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.__str__())
        super(Individual, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('individuals_detail', kwargs={'slug': self.slug})

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'