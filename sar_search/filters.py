import django_filters
from . import models
from shared_models import models as shared_models
from django import forms

chosen_js = {"class": "chosen-select-contains"}


class SpeciesFilter(django_filters.FilterSet):
    common_name_eng = django_filters.CharFilter(field_name='search_term', label="Species (any part of name...)", lookup_expr='icontains',
                                                widget=forms.TextInput())

    class Meta:
        model = models.Species
        fields = {
            'common_name_eng': ['exact'],
            'taxon': ['exact'],
            'cosewic_status': ['exact'],
            'sara_status': ['exact'],
            'nb_status': ['exact'],
            'ns_status': ['exact'],
            'pe_status': ['exact'],
            'sara_schedule': ['exact'],
            'province_range': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        SARA = 1
        NS = 2
        NB = 3
        PE = 4
        self.filters.get("nb_status").queryset = models.SpeciesStatus.objects.filter(used_for=NB)
        self.filters.get("ns_status").queryset = models.SpeciesStatus.objects.filter(used_for=NS)
        self.filters.get("pe_status").queryset = models.SpeciesStatus.objects.filter(used_for=PE)
        self.filters.get("sara_status").queryset = models.SpeciesStatus.objects.filter(used_for=SARA)
        self.filters.get("cosewic_status").queryset = models.SpeciesStatus.objects.filter(used_for=SARA)
        self.filters.get("province_range").queryset = shared_models.Province.objects.filter(id__in=[7, 1, 3, 4])


class RegionFilter(django_filters.FilterSet):
    class Meta:
        model = models.Region
        fields = {
            'name': ['icontains'],
        }

#
# class RiverFilter(django_filters.FilterSet):
#     class Meta:
#         model = shared_models.River
#         fields = {
#             'name': ['icontains'],
#         }
#
#
# class SampleFilter(django_filters.FilterSet):
#     class Meta:
#         model = models.Sample
#         fields = {
#             'season': ['exact'],
#             'site': ['exact'],
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         season = self.data.get("season")
#         if season:
#             site_choices = [(obj.id, str(obj)) for obj in models.RiverSite.objects.all() if obj.samples.filter(season=season).count() > 1]
#         else:
#             site_choices = [(obj.id, str(obj)) for obj in models.RiverSite.objects.all() if obj.samples.count() > 1]
#
#         self.filters["site"] = django_filters.ChoiceFilter(field_name="site", choices=site_choices, label="Site", widget=forms.Select(attrs=chosen_js))
