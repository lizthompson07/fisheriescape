# from accounts import models as account_models
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone

from . import models
import django_filters


class ProjectFilter(django_filters.FilterSet):
    FY_CHOICES = [("{}-{}".format(y, y + 1), "{}-{}".format(y, y + 1)) for y in
                  range(timezone.now().year - 2, timezone.now().year + 1)]
    # SECTION_CHOICES = [(None, "----"),]
    DIVISION_CHOICES = [(d.id, str(d)) for d in models.Division.objects.all()]
    SECTION_CHOICES = [(s.id, str(s)) for s in models.Section.objects.all()]
    YES_NO_CHOICES = [(True, "Yes"), (False, "No"), ]

    project_title = django_filters.CharFilter(field_name='project_title', lookup_expr='icontains')
    fiscal_year = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact', choices=FY_CHOICES)
    division = django_filters.ChoiceFilter(field_name='section__division', lookup_expr='exact', label="Division", choices=DIVISION_CHOICES)
    section = django_filters.ChoiceFilter(field_name='section', lookup_expr='exact', label="Section", choices=SECTION_CHOICES)
    submitted = django_filters.ChoiceFilter(field_name='submitted', lookup_expr='exact', label="Submitted?", choices=YES_NO_CHOICES)


