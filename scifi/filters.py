# from accounts import models as account_models
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone

from . import models
import django_filters


#
# class EntryFilter(django_filters.FilterSet):
#     # FY_CHOICES = [("{}-{}".format(y, y + 1), "{}-{}".format(y, y + 1)) for y in
#     #               range(timezone.now().year - 2, timezone.now().year + 1)]
#     # # SECTION_CHOICES = [(None, "----"),]
#     # DIVISION_CHOICES = [(d.id, str(d)) for d in models.Division.objects.all()]
#     # SECTION_CHOICES = [(s.id, str(s)) for s in models.Section.objects.all()]
#     #
#     # fiscal_year = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact', choices=FY_CHOICES)
#     # project_title = django_filters.CharFilter(field_name='project_title', lookup_expr='icontains')
#     # division = django_filters.ChoiceFilter(field_name='division', lookup_expr='exact', choices=DIVISION_CHOICES)
#     # section = django_filters.ChoiceFilter(field_name='section', lookup_expr='exact', choices=SECTION_CHOICES)
#
#     class Meta:
#         model = models.Entry
#         fields = {
#             'title': ['icontains'],
#             'sector': ['exact'],
#             'organization': ['exact'],
#             'created_by': ['exact'],
#         }

class LineObjectFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search line object (code, term, etc...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class TransactionFilter(django_filters.FilterSet):
    FY_CHOICES = [("{}-{}".format(y, y + 1), "{}-{}".format(y, y + 1)) for y in
                  range(timezone.now().year - 2, timezone.now().year + 1)]
    RC_CHOICES = [(obj.id, "{} ({})".format(obj.code, obj.name)) for obj in models.ResponsibilityCenter.objects.all().order_by("name")]


    fiscal_year = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact', choices=FY_CHOICES)
    project_code = django_filters.CharFilter(field_name='project__code', lookup_expr='icontains', label="Project code")
    responsibility_center = django_filters.ChoiceFilter(field_name='project__responsibility_center',
                                                        lookup_expr='exact', choices=RC_CHOICES, label="Responsibility center")
    supplier_description = django_filters.CharFilter(field_name='supplier_description', lookup_expr='icontains', label="Supplier description")
