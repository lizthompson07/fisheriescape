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


class OrgaFilter(django_filters.FilterSet):

    class Meta:
        model = models.Organization
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class ProgFilter(django_filters.FilterSet):

    class Meta:
        model = models.Program
        fields = ["prog_name", "proga_id", "orga_id",  "created_by", "created_date", ]


class ProgaFilter(django_filters.FilterSet):

    class Meta:
        model = models.ProgAuthority
        fields = ["proga_last_name", "proga_first_name", "created_by", "created_date", ]


class ProtFilter(django_filters.FilterSet):

    class Meta:
        model = models.Protocol
        fields = ["prog_id", "protc_id", "created_by", "created_date", ]


class ProtcFilter(django_filters.FilterSet):

    class Meta:
        model = models.ProtoCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class ProtfFilter(django_filters.FilterSet):

    class Meta:
        model = models.Protofile
        fields = ["prot_id", "created_by", "created_date", ]


class UnitFilter(django_filters.FilterSet):

    class Meta:
        model = models.UnitCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]

