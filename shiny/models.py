import os

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.dispatch import receiver


def img_file_name(instance, filename):
    img_name = 'shiny/{}'.format(instance.line.sample.id, filename)
    return img_name


class App(models.Model):
    title_en = models.CharField(max_length=255)
    title_fr = models.CharField(max_length=255, blank=True, null=True)
    description_en = models.CharField(max_length=255)
    description_fr = models.CharField(max_length=255, blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(blank=True, null=True, upload_to=img_file_name)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="shiny_apps")
    last_modified = models.DateTimeField(auto_now=True)

    @property
    def ttitle(self):
        # check to see if a french value is given
        if getattr(self, str(_("title_en"))):
            my_str = "{}".format(getattr(self, str(_("title_en"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = "{}".format(self.title_en)
        return my_str

    @property
    def tdescription(self):
        # check to see if a french value is given
        if getattr(self, str(_("description_en"))):
            my_str = "{}".format(getattr(self, str(_("description_en"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = "{}".format(self.description_en)
        return my_str

    def __str__(self):
        return self.ttitle

    class Meta:
        ordering = [_('title_en'), ]


@receiver(models.signals.post_delete, sender=App)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)


@receiver(models.signals.pre_save, sender=App)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_thumbnail = App.objects.get(pk=instance.pk).thumbnail
    except App.DoesNotExist:
        return False

    new_thumbnail = instance.thumbnail
    if not old_thumbnail == new_thumbnail:
        if os.path.isfile(old_thumbnail.path):
            os.remove(old_thumbnail.path)
