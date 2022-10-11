import django_filters
from django.db.models import Q

from django_filters.filters import OrderingFilter
from django import forms
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

from shared_models import models as shared_models
from masterlist import models as ml_models
from maret import models

chosen_js = {"class": "chosen-select-contains"}


class InteractionFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Search (Title of Interaction, Main results, Comments)"),
                                            lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Interaction
        fields = ["search_term", "interaction_type", "dfo_liaison", "main_topic", "external_organization",
                  "external_contact", "is_committee", "committee", "dfo_role", "other_dfo_participants", "species"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        interaction_choices = [obj for obj in models.Interaction.interaction_type_choices]
        interaction_choices.insert(0, (None, "All"))
        self.filters['dfo_liaison'] = django_filters.ModelMultipleChoiceFilter(
            queryset=shared_models.User.objects.all(),
            field_name='dfo_liaison',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )
        self.filters['main_topic'] = django_filters.ModelMultipleChoiceFilter(
            queryset=models.DiscussionTopic.objects.all(),
            field_name='main_topic',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )
        self.filters['external_organization'] = django_filters.ModelMultipleChoiceFilter(
            queryset=ml_models.Organization.objects.all(),
            field_name='external_organization',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )
        self.filters['external_contact'] = django_filters.ModelMultipleChoiceFilter(
            queryset=ml_models.Person.objects.all(),
            field_name='external_contact',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )
        self.filters['committee'] = django_filters.ModelMultipleChoiceFilter(
            queryset=models.Committee.objects.all(),
            field_name='committee',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )
        self.filters['other_dfo_participants'] = django_filters.ModelMultipleChoiceFilter(
            queryset=shared_models.User.objects.all(),
            field_name='other_dfo_participants',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )
        self.filters['species'] = django_filters.ModelMultipleChoiceFilter(
            queryset=models.Species.objects.all(),
            field_name='species',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )


class CommitteeFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Search (committee/working group name, role, and comments)"),
                                            lookup_expr='icontains', widget=forms.TextInput())

    external_chair_contact = django_filters.ModelMultipleChoiceFilter(
        queryset=ml_models.Person.objects.all(),
        method='external_chair_contact_filter',
        label=_('External chair or contact'),
        widget=forms.SelectMultiple(attrs=chosen_js),
    )

    class Meta:

        model = models.Committee
        fields = ['search_term', 'external_organization', 'external_chair_contact', 'branch', 'division', 'area_office',
                  'area_office_program', 'municipal_participation', 'provincial_participation', 'other_federal_participation', 'first_nation_participation', 'other_dfo_branch',
                  'other_dfo_branch', 'other_dfo_areas']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['external_organization'] = django_filters.ModelMultipleChoiceFilter(
            queryset=ml_models.Organization.objects.all(),
            field_name='external_organization',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )
        self.filters['dfo_role'] = django_filters.MultipleChoiceFilter(
            field_name='dfo_role', lookup_expr='exact',
            choices=models.ROLE_DFO_CHOICES,
            widget=forms.SelectMultiple(attrs=chosen_js),
            label=_("Highest level DFO participant"),
        )
        self.filters['dfo_liaison'] = django_filters.ModelMultipleChoiceFilter(
            queryset=models.User.objects.all(),
            field_name='dfo_liaison',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )
        self.filters['main_topic'] = django_filters.ModelMultipleChoiceFilter(
            queryset=models.DiscussionTopic.objects.all(),
            field_name='main_topic',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )
        self.filters['species'] = django_filters.ModelMultipleChoiceFilter(
            queryset=models.Species.objects.all(),
            field_name='species',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )

    def external_chair_contact_filter(self, queryset, name, value):
        if value:
            qureyset = queryset.filter(
                Q(external_chair__in=value) | Q(external_contact__in=value)
            )
        return queryset


class OrganizationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Search organizations (name, province, etc...)"),
                                            lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = ml_models.Organization
        fields = { }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['regions'] = django_filters.ModelMultipleChoiceFilter(
            queryset=shared_models.Region.objects.all(),
            field_name='regions',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )

        self.filters['ext_org__area'] = django_filters.ModelMultipleChoiceFilter(
            queryset=models.Area.objects.all(),
            label=_("Area(s)"),
            field_name='ext_org__area',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )

        self.filters['ext_org__category'] = django_filters.ModelMultipleChoiceFilter(
            queryset=models.OrgCategory.objects.all(),
            label=_("Category(s)"),
            field_name='ext_org__category',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )

        self.filters['grouping'] = django_filters.ModelMultipleChoiceFilter(
            queryset=ml_models.Grouping.objects.all(),
            field_name='grouping',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )
        self.filters['province'] = django_filters.ModelMultipleChoiceFilter(
            queryset=shared_models.Province.objects.all(),
            field_name='province',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )
        self.filters['committee'] = django_filters.ModelMultipleChoiceFilter(
            queryset=models.Committee.objects.all(),
            field_name='committee_ext_organization',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )
        self.filters['members'] = django_filters.ModelMultipleChoiceFilter(
            queryset=ml_models.Person.objects.all(),
            field_name='members__person',
            widget=forms.SelectMultiple(attrs=chosen_js),
        )


class PersonFilter(django_filters.FilterSet):
    class Meta:
        model = ml_models.Person
        fields = {
            'last_name': ['exact'],
            'memberships__role': ['icontains'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['memberships__role__icontains'].label = mark_safe(_("Organizational role <br>(any part of name)"))
        self.filters['organizations'] = django_filters.ModelMultipleChoiceFilter(field_name=_("organizations"),
                                                                         queryset=ml_models.Organization.objects.all(),
                                                                         widget=forms.SelectMultiple(attrs=chosen_js))
        self.filters["last_name"] = django_filters.CharFilter(field_name='search_term', label=_("Any part of name, or title"),
                                                              lookup_expr='icontains', widget=forms.TextInput())
