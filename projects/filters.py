from django.contrib.auth.models import User
from shared_models import models as shared_models

import django_filters


class ProjectFilter(django_filters.FilterSet):
    project_title = django_filters.CharFilter(field_name='project_title', lookup_expr='icontains')
    fiscal_year = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact')
    division = django_filters.ChoiceFilter(field_name='section__division', lookup_expr='exact', label="Division")
    section = django_filters.ChoiceFilter(field_name='section', lookup_expr='exact', label="Section")
    submitted = django_filters.ChoiceFilter(field_name='submitted', lookup_expr='exact', label="Submitted?")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all()]
        div_choices = [(d.id, str(d)) for d in shared_models.Division.objects.filter(branch=1)]
        sec_choices = [(s.id, str(s)) for s in shared_models.Section.objects.filter(division__branch=1)]
        yes_no_choices = [(True, "Yes"), (False, "No"), ]

        self.filters['fiscal_year'].choices = fy_choices
        self.filters['division'].choices = div_choices
        self.filters['section'].choices = sec_choices
        self.filters['submitted'].choices = yes_no_choices


class MySectionFilter(django_filters.FilterSet):
    fiscal_year = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact')
    project_title = django_filters.CharFilter(field_name='project_title', lookup_expr='icontains')
    staff = django_filters.ChoiceFilter(field_name='staff_members__user', lookup_expr='exact', label="Staff member")
    submitted = django_filters.ChoiceFilter(field_name='submitted', lookup_expr='exact', label="Submitted?")
    approved = django_filters.ChoiceFilter(field_name='section_head_approved', lookup_expr='exact', label="Approved by me?")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all()]
        user_choices = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in User.objects.all().order_by("last_name", "first_name")]
        yes_no_choices = [(True, "Yes"), (False, "No"), ]

        self.filters['fiscal_year'].choices = fy_choices
        self.filters['staff'].choices = user_choices
        self.filters['submitted'].choices = yes_no_choices
        self.filters['approved'].choices = yes_no_choices

