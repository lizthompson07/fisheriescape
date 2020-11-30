import django
import django_filters
from django.utils.translation import gettext as _

from . import models
import shared_models.models as shared_models


class InstFilter(django_filters.FilterSet):

    class Meta:
        model = models.Instrument
        fields = ["instc", "serial_number", "created_by", "created_date",]


class InstcFilter(django_filters.FilterSet):

    class Meta:
        model = models.InstrumentCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class InstdFilter(django_filters.FilterSet):

    class Meta:
        model = models.InstrumentDet
        fields = ["inst", "instdc", "valid", "created_by", "created_date", ]



class InstdcFilter(django_filters.FilterSet):

    class Meta:
        model = models.InstDetCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]
