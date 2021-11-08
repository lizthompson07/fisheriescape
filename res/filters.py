import django_filters
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from shared_models.models import FiscalYear
from . import utils
from .model_choices import application_status_choices
from .models import Achievement

chosen_js = {"class": "chosen-select-contains"}


class ApplicationFilter(django_filters.FilterSet):
    # search_term = django_filters.CharFilter(field_name='search_term', lookup_expr='icontains', label=_("Title / ref number"))
    application_id = django_filters.NumberFilter(field_name='id', lookup_expr='exact')
    fiscal_year = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact')
    region = django_filters.ChoiceFilter(field_name="section__division__branch__sector__region", label=_("Region"), lookup_expr='exact')
    section = django_filters.ChoiceFilter(field_name="section", label=_("Sector"), lookup_expr='exact')
    # has_process = django_filters.BooleanFilter(field_name='processes', lookup_expr='isnull', label=_("Has process?"), exclude=True)
    status = django_filters.ChoiceFilter(field_name='status', lookup_expr='exact', label=_("Status"),
                                         widget=forms.SelectMultiple(attrs=chosen_js), choices=application_status_choices)
    applicant = django_filters.ChoiceFilter(field_name="applicant", label=_("Applicant"), lookup_expr='exact')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['applicant'].field.widget.attrs = chosen_js

        region_choices = utils.get_region_choices()
        section_choices = utils.get_sector_choices()
        fy_choices = [(fy.id, str(fy)) for fy in FiscalYear.objects.filter(res_applications__isnull=False).distinct()]
        applicant_choices = [(u.id, str(u)) for u in User.objects.filter(res_applications__isnull=False).distinct()]
        self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact', choices=fy_choices,
                                                                  label=_("Fiscal year"), widget=forms.Select(attrs=chosen_js))
        self.filters['applicant'] = django_filters.ChoiceFilter(field_name='applicant', lookup_expr='exact', choices=applicant_choices,
                                                                label=_("Applicant name"), widget=forms.Select(attrs=chosen_js))
        self.filters['region'] = django_filters.ChoiceFilter(field_name="section__division__branch__sector__region", label=_("Region"), lookup_expr='exact',
                                                             choices=region_choices)
        self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=_("Section"), lookup_expr='exact',
                                                              choices=section_choices)

        try:
            if self.data["region"] != "":
                my_region_id = int(self.data["region"])
                section_choices = [my_set for my_set in utils.get_section_choices(region_filter=my_region_id)]
                self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=_("Section"), lookup_expr='exact', choices=section_choices)
        except KeyError:
            print('no data in filter')


# class SampleFilter(django_filters.FilterSet):
#     SeasonExact = django_filters.NumberFilter(field_name='year', label="From year", lookup_expr='exact')
#     MonthExact = django_filters.NumberFilter(field_name='month', label="From month", lookup_expr='exact')
#
#     class Meta:
#         model = models.Sample
#         fields = {
#             'id': ['exact'],
#             'station__site': ['exact'],
#             'station': ['exact'],
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.filters.get("station__site").label = "Site"
#
# class RegionFilter(django_filters.FilterSet):
#     search_term = django_filters.CharFilter(field_name='search_term', label=_("Search term"), lookup_expr='icontains',
#                                             widget=forms.TextInput())
#
#
class AchievementFilter(django_filters.FilterSet):
    date = django_filters.NumberFilter(field_name='date', label="Year", lookup_expr='startswith', widget=forms.NumberInput())

    class Meta:
        model = Achievement
        fields = {
            "id": ['exact'],
            "user": ['exact'],
            "category": ['exact'],
            "publication_type": ['exact'],
            "review_type": ['exact'],
            "date": ['exact'],
            "detail": ['icontains'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if utils.in_res_admin_group(self.request.user):
            user_choices = [(u.id, str(u)) for u in User.objects.filter(achievements__isnull=False).distinct()]
            self.filters['user'] = django_filters.ChoiceFilter(field_name='user', lookup_expr='exact', choices=user_choices,
                                                               label=_("User"), widget=forms.Select(attrs=chosen_js))
        else:
            del self.filters["user"]
