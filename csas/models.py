from django.db import models
#from shared_models import models as shared_models


# Create models
class CohHonorific(models.Model):
    coh_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

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
    honorific = models.ForeignKey(CohHonorific, models.DO_NOTHING)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    language = models.IntegerField()
    contact_type = models.ForeignKey(CotType, models.DO_NOTHING)    # should use IntegerField or ForeignKey
    notification_preference = models.ForeignKey(NotNotificationPreference, models.DO_NOTHING)    # should use IntegerField or ForeignKey
    phone = models.CharField(max_length=12)
    email = models.CharField(max_length=255)
    region = models.IntegerField()    # should use IntegerField or ForeignKey, we don't have region class
    section = models.ForeignKey(SecSector, models.DO_NOTHING)    # should use IntegerField or ForeignKey
    role = models.ForeignKey(RolRole, models.DO_NOTHING)    # should use IntegerField or ForeignKey
    expertise = models.CharField(max_length=100)
    cc_grad = models.IntegerField()    # what is TINYINT
    notes = models.CharField(max_length=400)   # what is MEDIUMTEXT

    def __str__(self):
        return "{}".format(self.last_name)
