from django.db import models

# Create your models here.


class doc(models.Model):

    item_name = models.CharField(max_length=255)
    section = models.ForeignKey('section', on_delete=models.DO_NOTHING)
    description = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.item_name

class section(models.Model):

    section_name = models.CharField(max_length=255)

    def __str__(self):
        return self.section_name
