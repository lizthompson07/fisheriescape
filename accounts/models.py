# from django.db import models
# from django.contrib.auth.models import User
# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
#
# # Create your models here.
#
# class Person(auth.models.User,auth.models.PermissionsMixin):
#
#     def __str__(self):
#         return "{}".format(self.username)
#
#     @property
#     def full_name(self):
#         return "{} {}".format(self.first_name, self.last_name)
#
#
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Person.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     Person.profile.save()
