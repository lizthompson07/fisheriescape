import django_filters
from . import models
from shared_models import models as shared_models
from django import forms

chosen_js = {"class": "chosen-select-contains"}

class MissionFilter(django_filters.FilterSet):
    mission_name = django_filters.CharFilter(field_name='search_term', label="Mission (name or number)", lookup_expr='icontains',
                                            widget=forms.TextInput())

    class Meta:
        model = shared_models.Cruise
        fields = {
            'institute': ['exact'],
            'mission_name': ['exact'],
            'vessel': ['exact'],
            'meds_id': ['exact'],
            'season': ['exact'],
        }
        # labels = {
        #     'mission_name': "Mission name",
        #     'mission_number': "Mission number",
        # }
