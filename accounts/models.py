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
    position_eng = models.CharField(max_length=255, blank=True, null=True)
    position_fre = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    language = models.IntegerField(choices=LANGUAGE_CHOICES, blank=True, null=True, verbose_name=_("language preference"))
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, blank=True, null=True,
                                verbose_name=_("Section"))

    def __str__(self):
        return "{}, {}".format(self.user.last_name, self.user.first_name)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def save(self, *args, **kwargs):
        self.full_name = "{} {}".format(self.user.first_name, self.user.last_name)

        super().save(*args, **kwargs)


@receiver(post_save,sender=User)
def create_user_profile(sender, instance, created, ** kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save,sender=User)
def save_user_profile(sender, instance, ** kwargs):
    instance.profile.save()
