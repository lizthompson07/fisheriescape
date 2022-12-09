import django_filters
from django import forms
from django.utils.translation import gettext, gettext_lazy

from shared_models import models as shared_models
from . import models

chosen_js = {"class": "chosen-select-contains"}


class SpeciesFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Species (any part of name...)", lookup_expr='icontains',
                                            widget=forms.TextInput())


class RiverFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="River (any part of name...)", lookup_expr='icontains',
                                            widget=forms.TextInput())
    site = django_filters.CharFilter(field_name='sites__name', label="Site (any part of name...)", lookup_expr='icontains',
                                     widget=forms.TextInput(), distinct=True)

    class Meta:
        model = shared_models.River
        fields = {
            'fishing_area': ['exact'],
        }


class SampleFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter("arrival_date__year", label=gettext_lazy("Year"))
    month = django_filters.NumberFilter("arrival_date__month", label=gettext_lazy("Month"))
    day = django_filters.NumberFilter("arrival_date__day", label=gettext_lazy("Day"))

    class Meta:
        model = models.Sample
        fields = {
            'id': ['exact'],
            'site__river': ['exact'],
            'site': ['exact'],
            'sample_type': ['exact'],
            'specimens__species': ['exact'],
            'monitoring_program': ['exact'],
            'site__river__fishing_area': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        season = self.data.get("year")
        if season and int(season) > 1:
            site_choices = [(obj.id, str(obj)) for obj in models.RiverSite.objects.filter(samples__arrival_date__year=season).distinct()]
            river_choices = [(obj.id, str(obj)) for obj in shared_models.River.objects.filter(sites__samples__arrival_date__year=season).distinct()]
        else:
            site_choices = [(obj.id, str(obj)) for obj in models.RiverSite.objects.filter(samples__isnull=False).distinct()]
            river_choices = [(obj.id, str(obj)) for obj in shared_models.River.objects.filter(sites__samples__isnull=False).distinct()]

        self.filters["site"] = django_filters.ChoiceFilter(field_name="site", choices=site_choices, label="Site", widget=forms.Select(attrs=chosen_js))
        self.filters["site__river"] = django_filters.ChoiceFilter(field_name="site__river", choices=river_choices, label="River")
        self.filters["specimens__species"].label = gettext("Species")
        self.filters["site__river__fishing_area"].label = gettext("Fishing area")


class SpecimenFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter("sample__arrival_date__year", label=gettext_lazy("Year"))
    month = django_filters.NumberFilter("sample__arrival_date__month", label=gettext_lazy("Month"))
    day = django_filters.NumberFilter("sample__arrival_date__day", label=gettext_lazy("Day"))

    class Meta:
        model = models.Specimen
        fields = {
            'id': ['exact'],
            'species': ['exact'],
            'tag_number': ['icontains'],
            'scale_id_number': ['icontains'],
            'sample__site__river': ['exact'],
            'sample__site': ['exact'],
            'sample__sample_type': ['exact'],
            'sample_id': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["sample_id"] = django_filters.NumberFilter(field_name="sample_id", label=gettext("Sample Id"))
        self.filters["scale_id_number__icontains"].label = gettext("Scale ID #")
        self.filters["tag_number__icontains"].label = gettext("Tag #")
        self.filters["sample__sample_type"].label = gettext("Sample type")
        self.filters["sample__site__river"].label = gettext("River")
        self.filters["sample__site"].label = gettext("Site")


class BiologicalDetailingFilter(django_filters.FilterSet):
    class Meta:
        model = models.BiologicalDetailing
        fields = {
            'id': ['exact'],
            'old_id': ['exact'],
            'species': ['exact'],
            'sample__site__river': ['exact'],
            'sample__site': ['exact'],
            'sample__sample_type': ['exact'],
            'sample_id': ['exact'],
        }