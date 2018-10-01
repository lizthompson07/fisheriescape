from django.db import models
from django.utils import timezone

# Create your models here.

def img_file_name(instance, filename):
    img_name = 'oceanography/{}'.format(filename)
    return img_name

class Doc(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)
    # url = models.TextField(null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to=img_file_name)
    date_modified = models.DateTimeField(default = timezone.now )

    def save(self,*args,**kwargs):
        self.date_modified  = timezone.now()
        return super().save(*args,**kwargs)


    def __str__(self):
        return self.item_name
