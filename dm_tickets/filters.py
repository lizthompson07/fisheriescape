import django_filters
from django import forms
from django.utils import timezone
from shared_models import models as shared_models
from . import models
from . import forms as ticket_forms


class TicketFilter(django_filters.FilterSet):
    section = django_filters.ChoiceFilter(field_name="section")
    search_term = django_filters.CharFilter(field_name='search_term', label="Key term (title, description, notes, Id):",
                                            lookup_expr='icontains', widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        section_choices = [(s.id, s.full_name) for s in shared_models.Section.objects.all().order_by(
            "division__branch__region", "division__branch", "division", "name")]
        self.filters['section'].choices = section_choices

    class Meta:
        model = models.Ticket
        fields = {
            'fiscal_year': ['exact'],
            'app': ['exact'],
            'status': ['exact'],
            # 'section': ['exact'],
        }


class FiscalFilter(django_filters.FilterSet):
    fiscal_year = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all()]
        self.filters['fiscal_year'].choices = fy_choices
