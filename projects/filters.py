from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import gettext as _
from shared_models import models as shared_models
import django_filters


class ProjectFilter(django_filters.FilterSet):
    project_title = django_filters.CharFilter(field_name='project_title', lookup_expr='icontains')
    fiscal_year = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact')
    region = django_filters.ModelChoiceFilter(field_name="section__division__branch__region", label=_("Region"), lookup_expr='exact',
                                              queryset=shared_models.Region.objects.filter(Q(id=1) | Q(id=2)))
    division = django_filters.ModelChoiceFilter(field_name='section__division', lookup_expr='exact', label=_("Division"),
                                                queryset=shared_models.Division.objects.filter(
                                                    Q(branch__region=1) | Q(branch__region=2)).order_by("branch__region", "name"))
    section = django_filters.ChoiceFilter(field_name='section', lookup_expr='exact', label=_("Section"))
    submitted = django_filters.ChoiceFilter(field_name='submitted', lookup_expr='exact', label=_("Submitted?"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



        section_choices = [(s.id, s.full_name) for s in shared_models.Section.objects.filter(
                               Q(division__branch__region=1) | Q(division__branch__region=2)
                           ).order_by("division__branch__region", "division__branch", "division", "name")]
        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all()]
        yes_no_choices = [(True, "Yes"), (False, "No"), ]

        self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=fy_choices)
        self.filters['submitted'] = django_filters.ChoiceFilter(field_name='submitted', lookup_expr='exact', choices=yes_no_choices)
        self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=_("Section"),
                                                              lookup_expr='exact', choices=section_choices)
        # self.filters['division'] = django_filters.ChoiceFilter(field_name='section__division', lookup_expr='exact', choices=div_choices)

        try:
            # if there is a filter on region, filter the division and section filter accordingly
            if self.data["region"] != "":
                self.filters["division"].queryset = shared_models.Division.objects.filter(branch__region=self.data["region"])
                section_choices = [(s.id, s.full_name) for s in shared_models.Section.objects.filter(
                                       division__branch__region=self.data["region"]
                                   ).order_by("division__branch__region", "division__branch", "division", "name")]
                self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=_("Section"),
                                                                      lookup_expr='exact', choices=section_choices)

            # if there is a filter on division, filter the section filter accordingly
            if self.data["division"] != "":
                section_choices = [(s.id, s.full_name) for s in shared_models.Section.objects.filter(
                                       division=self.data["division"]
                                   ).order_by("division__branch__region", "division__branch", "division", "name")]
                self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=_("Section"),
                                                                      lookup_expr='exact', choices=section_choices)
        except KeyError:
            print('no data in filter')

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all()]
    #     div_choices = [(d.id, str(d)) for d in shared_models.Division.objects.filter(branch=1)]
    #     sec_choices = [(s.id, str(s)) for s in shared_models.Section.objects.filter(division__branch=1)]
    #     yes_no_choices = [(True, "Yes"), (False, "No"), ]
    #
    #     self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=fy_choices)
    #     self.filters['division'] = django_filters.ChoiceFilter(field_name='section__division', lookup_expr='exact', choices=div_choices)
    #     self.filters['section'] = django_filters.ChoiceFilter(field_name='section', lookup_expr='exact', choices=sec_choices)
    #     self.filters['submitted'] = django_filters.ChoiceFilter(field_name='submitted', lookup_expr='exact', choices=yes_no_choices)
    #
    #     # if there is a filter on division, filter the section filter accordingly
    #     try:
    #         if self.data["division"] != "":
    #             sec_choices = [(s.id, str(s)) for s in shared_models.Section.objects.filter(division__branch=1)]
    #             self.filters['section'] = django_filters.ChoiceFilter(field_name='section', lookup_expr='exact', choices=sec_choices)
    #
    #     except KeyError:
    #         print('no data in filter')


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

        self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=fy_choices)
        self.filters['staff'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=user_choices)
        self.filters['submitted'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=yes_no_choices)
        self.filters['approved'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=yes_no_choices)
