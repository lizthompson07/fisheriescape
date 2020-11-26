from django.db import models

# Create your models here.
from shared_models import models as shared_models
from django.db import models
from django.utils.translation import gettext_lazy as _


class BioLookup(shared_models.Lookup):

    class Meta:
        abstract = True

    created_by = models.CharField(max_length=32, verbose_name=_("Created By"))
    created_date = models.DateField(verbose_name=_("Created Date"))


class InstDetCode(BioLookup):
    # instdc tag
    pass


class InstrumentCode(BioLookup):
    # instc tag
    pass


class Instrument(models.Model):
    # inst tag
    instc = models.ForeignKey('InstrumentCode', on_delete=models.DO_NOTHING, verbose_name=_("Instrument Code"),
                              related_name="instrument_code")
    serial_number = models.CharField(max_length=250, verbose_name=_("Serial Number"))
    comments = models.CharField(max_length=2000, verbose_name=_("Comments"))
    created_by = models.CharField(max_length=32, verbose_name=_("Created By"))
    created_date = models.DateField(verbose_name=_("Created Date"))
    pass
