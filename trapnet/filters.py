import django_filters
from django.utils.translation import gettext

from . import models
from shared_models import models as shared_models
from django import forms

chosen_js = {"class": "chosen-select-contains"}

class SpeciesFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Species (any part of name...)", lookup_expr='icontains',
                                            widget=forms.TextInput())


class RiverFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="River (any part of name...)", lookup_expr='icontains',
                                            widget=forms.TextInput())


class SampleFilter(django_filters.FilterSet):
    class Meta:
        model = models.Sample
        fields = {
            'season': ['exact'],
            'site': ['exact'],
            'sample_type': ['exact'],
            'observations__species': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        season = self.data.get("season")
        if season:
            site_choices = [(obj.id, str(obj)) for obj in models.RiverSite.objects.all() if obj.samples.filter(season=season).count() > 1]
        else:
            site_choices = [(obj.id, str(obj)) for obj in models.RiverSite.objects.all() if obj.samples.count() > 1]

        self.filters["site"] = django_filters.ChoiceFilter(field_name="site", choices=site_choices, label="Site", widget=forms.Select(attrs=chosen_js))



class ObservationFilter(django_filters.FilterSet):
    class Meta:
        model = models.Observation
        fields = {
            'species': ['exact'],
            'tag_number': ['iexact'],
            'scale_id_number': ['iexact'],
            'sample__site': ['exact'],
            'sample_id': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["sample_id"] = django_filters.NumberFilter(field_name="sample_id", label=gettext("Sample Id"))
