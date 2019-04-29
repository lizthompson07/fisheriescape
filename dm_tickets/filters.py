import django_filters
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from shared_models import models as shared_models
from . import models
from . import forms as ticket_forms


class TicketFilter(django_filters.FilterSet):
    section = django_filters.ChoiceFilter(field_name="section")
    dm_assigned = django_filters.ChoiceFilter(field_name="dm_assigned")
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term (Id, title, etc.):",
                                            lookup_expr='icontains', widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        section_choices = [(s.id, s.full_name) for s in shared_models.Section.objects.all().order_by(
            "division__branch__region", "division__branch", "division", "name")]
        staff_choices = [(dm.id, "{} {}".format(dm.first_name, dm.last_name)) for dm in User.objects.filter(is_staff=True)]
        self.filters['section'] = django_filters.ChoiceFilter(field_name="section", choices=section_choices)
        self.filters['dm_assigned'] = django_filters.ChoiceFilter(field_name="dm_assigned", choices=staff_choices, label="Ticket assigned to")
    class Meta:
        model = models.Ticket
        fields = {
            'fiscal_year': ['exact'],
            'app': ['exact'],
            'status': ['exact'],
        }





class FiscalFilter(django_filters.FilterSet):
    fiscal_year = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all()]
        self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact',
                                                                  choices=fy_choices)
