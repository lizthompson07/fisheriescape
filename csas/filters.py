import django_filters
from django_filters import FilterSet
from django import forms

from . import models


class ContactFilter(FilterSet):
    class Meta:
        model = models.ConContact
        fields = ['last_name', 'first_name', 'contact_type', 'region']


class MeetingFilter(FilterSet):
    start_date = django_filters.ChoiceFilter(field_name='start_date', lookup_expr='exact')

    class Meta:
        model = models.MetMeeting
        fields = ['start_date', 'title_en', 'process_type', 'lead_region']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        dates = [(y[0], str(y[0])) for y in models.MetMeeting.objects.all().values_list('start_date').distinct()]
        self.filters['start_date'] = django_filters.ChoiceFilter(field_name='start_date', lookup_expr='exact', choices=dates)


class RequestFilter(FilterSet):
    # start_date = django_filters.ChoiceFilter(field_name='start_date', lookup_expr='exact')
    region = django_filters.ChoiceFilter(field_name='region', lookup_expr='exact')

    class Meta:
        model = models.ReqRequest
        # fields = ['start_date', 'title_en', 'process_type', 'lead_region']
        fields = ['region', 'client_sector', 'title', 'client_name', 'funding']
        # fields = {'finding': ['Yes', 'No'],}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # dates = [(y[0], str(y[0])) for y in models.MetMeeting.objects.all().values_list('start_date').distinct()]
        # self.filters['start_date'] = django_filters.ChoiceFilter(field_name='start_date', lookup_expr='exact', choices=dates)
