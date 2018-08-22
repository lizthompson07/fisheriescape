import django_filters
from . import models
from accounts import models as account_models
from django import forms

class ResourceFilter(django_filters.FilterSet):
    # SeasonExact = django_filters.NumberFilter(field_name='season', label="From year", lookup_expr='exact', widget= forms.NumberInput(attrs={'style':"width: 4em"}))
    # search_term = django_filters.CharFilter(label="People", lookup_expr='icontains')

    class Meta:
        model = models.Resource
        fields = {
            'title_eng':['icontains'],
            'section':['exact'],
            'people':['exact'],
            'status':['exact'],
        }

        # def __init__(self, *args, **kwargs):
        #     super(SampleFilter, self).__init__(*args, **kwargs)
        #     self.filters['people'].extra.update(
        #         {'empty_label': 'All Manufacturers'})



class PersonFilter(django_filters.FilterSet):

    class Meta:
        model = models.Person
        fields = {
            'full_name': ['icontains'],
        }

class KeywordFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(label="Keyword Search Term", lookup_expr='icontains')

    # class Meta:
    #     model = models.Keyword
    #     fields = {
    #         'text_value_eng': ['icontains'],
    #         'details': ['icontains'],

        #     'keyword_domain': ['exact'],
        #     'is_taxonomic': ['exact'],
        # }

class CitationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(label="Citation Search Term", lookup_expr='icontains')

    # class Meta:
    #     model = models.Citation
    #     fields = {
    #         'publication': ['exact'],
    #     }
