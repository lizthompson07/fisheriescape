from django.db import models
from django.contrib.auth.models import User
from shared_models import models as shared_models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils.translation import gettext as _

# Choices for language
ENG = 1
FRE = 2
LANGUAGE_CHOICES = (
    (ENG, 'English'),
    (FRE, 'French'),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    position_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("position (English)"))
    position_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("position (French)"))
    phone = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("phone (office)"))
    language = models.IntegerField(choices=LANGUAGE_CHOICES, blank=True, null=True, verbose_name=_("language preference"))
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, blank=True, null=False,
                                verbose_name=_("Section"))
    retired = models.BooleanField(default=False)

    def __str__(self):
        return "{}, {}".format(self.user.last_name, self.user.first_name)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def save(self, *args, **kwargs):
        self.full_name = "{} {}".format(self.user.first_name, self.user.last_name)

        super().save(*args, **kwargs)


class Announcement(models.Model):
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    subject_en = models.CharField(max_length=150)
    subject_fr = models.CharField(max_length=150, blank=True, null=True)
    message_en = models.TextField()
    message_fr = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-valid_from', ]

    @property
    def tsubject(self):
        # check to see if a french value is given
        if getattr(self, str(_("subject_en"))):
            return "{}".format(getattr(self, str(_("subject_en"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.subject_en)

    @property
    def tmessage(self):
        # check to see if a french value is given
        if getattr(self, str(_("message_en"))):
            return "{}".format(getattr(self, str(_("message_en"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.message_en)