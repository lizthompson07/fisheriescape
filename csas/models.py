from django.db import models
from shared_models import models as shared_models


# Create your models here.
class CotType(models.Model):
    cot_id = models.models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

    def __str__(self):
        return "{}".format(self.name)