# from accounts import models as account_models
from django.contrib.auth.models import User
from django import forms
from django.utils.translation import gettext as _
from . import models
import django_filters
from shared_models import models as shared_models

chosen_js = {"class": "chosen-select-contains"}

#--------------------Filters----------------------
# Purpose: filterset_class for SearchView (views.py)
# Input: 
# Output: Filters bar on Search Page
#-------------------------------------------------  
class pssiFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(field_name='search_term', label=_("Keyword"), lookup_expr='icontains',
                                            widget=forms.TextInput())

    # --------------------------These filters have not been implemented yet-----------------------------------

    # This will allow users to select a field to filter by in the possible_column_values                                     
    # column = django_filters.ChoiceFilter(field_name="column", label = _("Column"), lookup_expr='exact',
    #                                           widget=forms.Select(attrs=chosen_js))

    # This will search the values in the specified column and return distinct values to filter by
    # possible_column_values = django_filters.ChoiceFilter(field_name="possible_values", lookup_expr='exact',
    #                                      widget=forms.Select(attrs=chosen_js))

    #---------------------------------------------------------------------------------------------------------
    
    # Placeholder for filtering by topic - real definition happens on the fly in __init__ method
    topic = django_filters.ChoiceFilter(field_name="topic", label=_("Topic"), lookup_expr='exact',
                                              widget=forms.Select(attrs=chosen_js),)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # For loop to grab the names of tags for the topic filter
        # Generates a list of 2-element tuples with the format: (searchFor, displayValue). This format needed for choices parameter in the next lines
        topic_choices = [(t.tag_ID, t.tag_Name) for t in
                           models.Tag.objects.all().order_by("tag_Name")]

        # Sets the topic filter to list off the choices, generated above
        self.filters['topic'] = django_filters.ChoiceFilter(field_name="topic",
                                                              lookup_expr='exact', choices=topic_choices)


        # # if there is a filter on section, filter the people filter accordingly
        # try:
        #     if self.data["section"] != "":
        #         self.filters["person"].queryset = models.Person.objects.filter(resource__section_id=self.data["section"]).distinct()
        #     elif self.data["region"] != "":
        #         SECTION_CHOICES = [(s.id, s.full_name) for s in
        #                            shared_models.Section.objects.filter(division__branch__region_id=self.data["region"]).order_by(
        #                                "division__branch__region", "division__branch", "division", "name")]
        #         self.filters["section"] = django_filters.ChoiceFilter(field_name="section", label=_("Section"), lookup_expr='exact',
        #                                                               choices=SECTION_CHOICES)
        #         self.filters["person"].queryset = models.Person.objects.filter(
        #             resource__section__division__branch__region=self.data["region"]).distinct()
        # except KeyError:
        #     print('no data in filter')


# class PersonFilter(django_filters.FilterSet):
#     search_term = django_filters.CharFilter(field_name='search_term', label=_("Name or email or person"), lookup_expr='icontains',
#                                             widget=forms.TextInput())


# class KeywordFilter(django_filters.FilterSet):
#     search_term = django_filters.CharFilter(label="Keyword Search Term", lookup_expr='icontains')


# class CitationFilter(django_filters.FilterSet):
#     search_term = django_filters.CharFilter(label="Citation Search Term", lookup_expr='icontains')
