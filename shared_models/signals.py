from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver

from .models import Person


@receiver(models.signals.post_save, sender=User)
def save_person_on_user_save(sender, instance, created, **kwargs):
    qs = Person.objects.filter(email__iexact=instance.email)
    person = None
    if not qs.exists():
        person = Person.objects.create(email=instance.email)
    elif qs.count() == 1:
        person = Person.objects.get(email__iexact=instance.email)
    else:
        print("warning! duplicate email in system:", instance.email, instance.username)

    if person:
        person.dmapps_user = instance
        person.save()


@receiver(models.signals.pre_delete, sender=User)
def abandon_person_on_user_delete(sender, instance, **kwargs):
    # when a user is deleted, we want to keep the Person instance so they will have to be separated
    if hasattr(instance, "contact"):
        p = instance.contact
        p.dmapps_user = None
        p.save()
