from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from . import models

#
# @receiver(post_save, sender=User)
# def auto_delete_file_on_change(sender, instance, **kwargs):
#     """
#     Following the creation of a new user, get/create an instance of Person
#     """
#
#     # using the email address, see if there is an existing person
#     qs = models.Person.objects.filter(email_1__icontains=instance.email)
#     if not qs.exists():
#         models.Person.objects.create(
#             first_name=instance.first_name,
#             email_1=instance.email,
#             last_name=instance.last_name,
#             last_modified_by=instance
#         )
#     else:
#         person = qs.first()
#         person.first_name = instance.first_name
#         person.last_name = instance.last_name
#         person.last_modified_by = instance
#         person.save()

