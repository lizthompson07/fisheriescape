import django_filters
from django import forms
from django.utils import timezone
from shared_models import models as shared_models
from . import models
from . import forms as ticket_forms


class TicketFilter(django_filters.FilterSet):
    SECTION_CHOICES = [(s.id, s.full_name) for s in shared_models.Section.objects.all().order_by("division__branch__region", "division__branch", "division", "name")]

    section = django_filters.ChoiceFilter(field_name="section", choices=SECTION_CHOICES)
    search_term = django_filters.CharFilter(field_name='search_term', label="Key term (title, description, notes, Id):",
                                            lookup_expr='icontains', widget=forms.TextInput())
    class Meta:
        model = models.Ticket
        fields = {
            'fiscal_year': ['exact'],
            'status': ['exact'],
            # 'section': ['exact'],
        }


class FiscalFilter(django_filters.FilterSet):
    FY_CHOICES = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all()]
    fiscal_year = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact', choices=FY_CHOICES)
