from django.db import models
from django.utils.translation import gettext_lazy as _

from shared_models import models as shared_models


# Create models
class CohHonorific(models.Model):
    coh_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, verbose_name="Honorific")

    def __str__(self):
        return "{}".format(self.name)


class CotType(models.Model):
    cot_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)


class LanLanguage(models.Model):
    lan_id = models.AutoField(primary_key=True)    # should this be AutoField or fixed?
    name = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)


class NotNotificationPreference(models.Model):
    not_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)


class RolRole(models.Model):
    role_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)


class SecSector(models.Model):
    sec_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)


class ConContact(models.Model):
    con_id = models.AutoField(primary_key=True)
    honorific = models.ForeignKey(CohHonorific, on_delete=models.DO_NOTHING)
    first_name = models.CharField(max_length=100, help_text=_("Some help here"))
    last_name = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    language = models.ForeignKey(LanLanguage, on_delete=models.DO_NOTHING)
    contact_type = models.ForeignKey(CotType, on_delete=models.DO_NOTHING)    # should use IntegerField or ForeignKey
    notification_preference = models.ForeignKey(NotNotificationPreference, models.DO_NOTHING)    # should use IntegerField or ForeignKey
    phone = models.CharField(max_length=12)
    email = models.CharField(max_length=255)
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING)
    section = models.ForeignKey(SecSector, on_delete=models.DO_NOTHING)    # should use IntegerField or ForeignKey
    role = models.ForeignKey(RolRole, on_delete=models.DO_NOTHING)    # should use IntegerField or ForeignKey
    expertise = models.CharField(max_length=100)
    cc_grad = models.BooleanField()    # what is TINYINT
    notes = models.TextField()   # what is MEDIUMTEXT

    def __str__(self):
        return "{}".format(self.last_name)
