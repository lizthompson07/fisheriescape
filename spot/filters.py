# from accounts import models as account_models
from gettext import gettext as _
from django import forms
import django_filters
from django.db.models import Q

from . import models
from masterlist import models as ml_models
from shared_models import models as shared_models
YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class OrganizationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search name",
                                            lookup_expr='icontains', widget=forms.TextInput())
    province = django_filters.ModelMultipleChoiceFilter(field_name='province', lookup_expr='exact', queryset=shared_models.Province.objects.all())
    grouping = django_filters.ModelMultipleChoiceFilter(field_name='grouping', lookup_expr='exact', queryset=ml_models.Grouping.objects.all())
    regions = django_filters.ModelMultipleChoiceFilter(field_name='regions', lookup_expr='exact', queryset=shared_models.Region.objects.all())  #queryset=shared_models.Region.objects.filter(Q(id=1)|Q(id=2))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class PersonFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search",
                                            lookup_expr='icontains', widget=forms.TextInput())
    membership = django_filters.ModelMultipleChoiceFilter(field_name='organizations', lookup_expr='exact', queryset=ml_models.Organization.objects.all())


class ProjectFilter(django_filters.FilterSet):

    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())
    organization = django_filters.ChoiceFilter(field_name='organization', lookup_expr='exact')
    fiscal = django_filters.ModelChoiceFilter(field_name='start_year', lookup_expr='exact', queryset=shared_models.FiscalYear.objects.all())
    status = django_filters.ModelChoiceFilter(field_name='status', lookup_expr='exact', queryset=models.Status.objects.all())
    program = django_filters.ModelChoiceFilter(field_name='program', lookup_expr='exact', queryset=models.Program.objects.all())
    watershed = django_filters.ModelChoiceFilter(field_name='watersheds', lookup_expr='exact', queryset=models.Watershed.objects.all())
    # species = django_filters.ModelChoiceFilter(field_name='spp', lookup_expr='exact', queryset=models.Species.objects.all())
    regions = django_filters.ModelMultipleChoiceFilter(field_name='regions', lookup_expr='exact', queryset=shared_models.Region.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        org_choices = [(o.id, str(o)) for o in ml_models.Organization.objects.all() if o.projects.count() > 0]
        self.filters["organization"] = django_filters.ChoiceFilter(field_name='organization', lookup_expr='exact', choices=org_choices)

