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
# Input: search_term field & field_list defined in SearchView
# Output: Filters bar on Search Page
#-------------------------------------------------  
class pssiFilter(django_filters.FilterSet):
    # lookup_expr = 'icontains' means that it's checking if the keyword is contained (i: case insensitive) in search_term from SearchView
    keyword = django_filters.CharFilter(field_name='search_term', label=_("Keyword"), lookup_expr='icontains',
                                            widget=forms.TextInput())

    # --------------------------These filters have not been fully implemented yet-----------------------------------

    # This will allow users to select a field to filter by in the possible_column_values
    # Choices for fields in DataAsset table defined in __init__ method  
    # NOTE: This currently tries to filter by field name, which isn't possible currently
    #       This filter shouldn't actually be applied to the data, but it should be applied as a variable to possible_column_values e.g. choosing from dropdown -> colChoice = "<Column Name>" 
                                   
    # column = django_filters.ChoiceFilter(field_name="column", label = _("Column"), lookup_expr='exact',
    #                                           widget=forms.Select(attrs=chosen_js))

    # This will search the values in the specified column i.e. colChoice, and return distinct values to filter by 
    # NOTE: Hasn't been implemented yet, but it should take the colChoice from the column filter and list distinct values in a dropdown
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
        
        # If field is not a key from another table, search for field by name, display verbose name (human-readable names defined in models.py)
        col_choices = []
        for field in models.DataAsset._meta.get_fields():
            if not field.is_relation:
                col_choices.append((field.name, field.verbose_name))

        # Assign the defined choices to dropdowns in the filters
        self.filters['topic'] = django_filters.ChoiceFilter(field_name="topic", lookup_expr='exact', choices=topic_choices)

        # Commented out until functional
        # self.filters['column'] = django_filters.ChoiceFilter(field_name="column", lookup_expr='exact', choices=col_choices)


    