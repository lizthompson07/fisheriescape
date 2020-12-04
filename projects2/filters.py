from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models
import django_filters
from . import utils
from . import views
from . import models

chosen_js = {"class": "chosen-select-contains"}


class StaffFilter(django_filters.FilterSet):
    fiscal_year = django_filters.ChoiceFilter(field_name='project__year', lookup_expr='exact')
    region = django_filters.ChoiceFilter(field_name="project__section__division__branch__region", label=_("Region"), lookup_expr='exact')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        region_choices = utils.get_region_choices()
        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all() if fy.projects.count() > 0]
        yes_no_choices = [(True, "Yes"), (False, "No"), ]
        self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='project__year', lookup_expr='exact', choices=fy_choices)
        self.filters['region'] = django_filters.ChoiceFilter(field_name="project__section__division__branch__region", label=_("Region"),
                                                             lookup_expr='exact', choices=region_choices)
        self.filters['project__submitted'].label = "Has the project been submitted?"

    class Meta:
        model = models.Staff
        fields = {
            'employee_type': ['exact'],
            'is_lead': ['exact'],
        }

#
# class AdminProjectProgramFilter(django_filters.FilterSet):
#     # fiscal_year = django_filters.ChoiceFilter(field_name='_year', lookup_expr='exact')
#     # region = django_filters.ChoiceFilter(field_name="section__division__branch__region", label=_("Region"), lookup_expr='exact')
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         region_choices = utils.get_region_choices()
#         fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all() if fy.projects.count() > 0]
#         yes_no_choices = [(True, "Yes"), (False, "No"), ]
#         self.filters['year'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=fy_choices)
#         self.filters['section__division__branch__region'] = django_filters.ChoiceFilter(field_name="section__division__branch__region",
#                                                                                         label=_("Region"),
#                                                                                         lookup_expr='exact', choices=region_choices)
#
#     class Meta:
#         model = models.Project
#         fields = {
#             'year': ['exact'],
#             'section__division__branch__region': ['exact'],
#             'project_title': ['icontains'],
#         }
#
#
# class AdminSubmittedUnapprovedFilter(django_filters.FilterSet):
#     # fiscal_year = django_filters.ChoiceFilter(field_name='_year', lookup_expr='exact')
#     # region = django_filters.ChoiceFilter(field_name="section__division__branch__region", label=_("Region"), lookup_expr='exact')
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         region_choices = utils.get_region_choices()
#         fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all() if fy.projects.count() > 0]
#         yes_no_choices = [(True, "Yes"), (False, "No"), ]
#         self.filters['year'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=fy_choices)
#         self.filters['section__division__branch__region'] = django_filters.ChoiceFilter(field_name="section__division__branch__region",
#                                                                                         label=_("Region"),
#                                                                                         lookup_expr='exact', choices=region_choices)
#
#     class Meta:
#         model = models.Project
#         fields = {
#             'year': ['exact'],
#             'section__division__branch__region': ['exact'],
#         }
#
#
# class MySectionFilter(django_filters.FilterSet):
#     fiscal_year = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact')
#     project_title = django_filters.CharFilter(field_name='project_title', lookup_expr='icontains')
#     staff = django_filters.ChoiceFilter(field_name='staff_members__user', lookup_expr='exact', label="Staff member")
#     submitted = django_filters.ChoiceFilter(field_name='submitted', lookup_expr='exact', label="Submitted?")
#
#     # approved = django_filters.ChoiceFilter(field_name='approved', lookup_expr='exact', label="Approved by me?")
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all() if fy.projects.count() > 0]
#         user_choices = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in User.objects.all().order_by("last_name", "first_name")]
#         yes_no_choices = [(True, "Yes"), (False, "No"), ]
#
#         self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=fy_choices)
#         self.filters['staff'] = django_filters.ChoiceFilter(field_name='staff_members__user', lookup_expr='exact', choices=user_choices,
#                                                             widget=forms.Select(attrs=chosen_js))
#         self.filters['submitted'] = django_filters.ChoiceFilter(field_name='submitted', lookup_expr='exact', choices=yes_no_choices)
#
#         if "my-section" in str(kwargs["request"]):
#             self.filters['approved'] = django_filters.ChoiceFilter(field_name='approved', lookup_expr='exact',
#                                                                    label="Approved by me?", choices=yes_no_choices)
#         elif "my-division" in str(kwargs["request"]):
#             self.filters['sh_approved'] = django_filters.ChoiceFilter(field_name='approved', lookup_expr='exact',
#                                                                       label="Approved by section head?", choices=yes_no_choices)
#             self.filters['approved'] = django_filters.ChoiceFilter(field_name='manager_approved', lookup_expr='exact',
#                                                                    label="Approved by me?", choices=yes_no_choices)
#         elif "my-branch" in str(kwargs["request"]):
#             self.filters['dm_approved'] = django_filters.ChoiceFilter(field_name='manager_approved', lookup_expr='exact',
#                                                                       label="Approved by division manager?", choices=yes_no_choices)
#             self.filters['approved'] = django_filters.ChoiceFilter(field_name='rds_approved', lookup_expr='exact',
#                                                                    label="Approved by me?", choices=yes_no_choices)
#
#
# class SectionFilter(django_filters.FilterSet):
#     class Meta:
#         model = models.Project
#         fields = {
#             'year': ['exact'],
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all() if fy.projects.count() > 0]
#         self.filters['year'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=fy_choices,
#                                                            label=_("Please select a fiscal year:"))
#
#
# class MyProjectFilter(django_filters.FilterSet):
#     class Meta:
#         model = models.Project
#         fields = {
#             'year': ['exact'],
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all() if fy.projects.count() > 0]
#         self.filters['year'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=fy_choices,
#                                                            label=_("Please select a fiscal year:"))

#
class FunctionalGroupFilter(django_filters.FilterSet):
    class Meta:
        model = models.FunctionalGroup
        fields = {
            'name': ['exact'],
            'theme': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all() if fy.projects.count() > 0]
        self.filters['name'] = django_filters.CharFilter(field_name='search_term', label=_("Name"), lookup_expr='icontains',
                                            widget=forms.TextInput())


class ProjectCodeFilter(django_filters.FilterSet):
    class Meta:
        model = shared_models.Project
        fields = {
            'name': ['icontains'],
            'code': ['icontains'],
        }
class RCFilter(django_filters.FilterSet):
    class Meta:
        model = shared_models.ResponsibilityCenter
        fields = {
            'name': ['icontains'],
            'code': ['icontains'],
        }