from django.contrib.auth.models import User
from shared_models import models as shared_models

from . import models
import django_filters


class ProjectFilter(django_filters.FilterSet):
    FY_CHOICES = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all()]
    DIVISION_CHOICES = [(d.id, str(d)) for d in shared_models.Division.objects.filter(branch=1)]
    SECTION_CHOICES = [(s.id, str(s)) for s in shared_models.Section.objects.filter(division__branch=1)]
    YES_NO_CHOICES = [(True, "Yes"), (False, "No"), ]

    project_title = django_filters.CharFilter(field_name='project_title', lookup_expr='icontains')
    fiscal_year = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=FY_CHOICES)
    division = django_filters.ChoiceFilter(field_name='section__division', lookup_expr='exact', label="Division", choices=DIVISION_CHOICES)
    section = django_filters.ChoiceFilter(field_name='section', lookup_expr='exact', label="Section", choices=SECTION_CHOICES)
    submitted = django_filters.ChoiceFilter(field_name='submitted', lookup_expr='exact', label="Submitted?", choices=YES_NO_CHOICES)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # if there is a filter on section, filter the people filter accordingly
    #     try:
    #         if self.data["section"] != "":
    #             self.filters["person"].queryset = models.Person.objects.filter(resource__section_id=self.data["section"]).distinct()
    #         elif self.data["division"] != "":
    #             self.filters["section"].queryset = models.Section.objects.filter(region=self.data["region"]).distinct()
    #             self.filters["person"].queryset = models.Person.objects.filter(resource__section__region=self.data["region"]).distinct()
    #     except KeyError:
    #         print('no data in filter')

class MySectionFilter(django_filters.FilterSet):
    FY_CHOICES = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all()]
    USER_CHOICES = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in User.objects.all().order_by("last_name", "first_name")]
    YES_NO_CHOICES = [(True, "Yes"), (False, "No"), ]

    fiscal_year = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=FY_CHOICES)
    project_title = django_filters.CharFilter(field_name='project_title', lookup_expr='icontains')
    staff = django_filters.ChoiceFilter(field_name='staff_members__user', lookup_expr='exact', choices=USER_CHOICES, label="Staff member")
    submitted = django_filters.ChoiceFilter(field_name='submitted', lookup_expr='exact', label="Submitted?", choices=YES_NO_CHOICES)
    approved = django_filters.ChoiceFilter(field_name='section_head_approved', lookup_expr='exact', label="Approved by me?", choices=YES_NO_CHOICES)

