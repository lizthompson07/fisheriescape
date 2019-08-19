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
            'sara_schedule': ['exact'],
            'province_range': ['exact'],
        }


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
