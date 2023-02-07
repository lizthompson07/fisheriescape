# from accounts import models as account_models
import django_filters
from django import forms
from django.utils.translation import gettext as _

from shared_models import models as shared_models
from . import models

chosen_js = {"class": "chosen-select-contains"}


class ResourceFilter(django_filters.FilterSet):
    class Meta:
        model = models.Resource
        fields = {
            'review_status': ['exact'],
        }

    search_term = django_filters.CharFilter(field_name='search_term', label=_("Search term (title, uuid, ...)"), lookup_expr='icontains',
                                            widget=forms.TextInput())
    region = django_filters.ModelChoiceFilter(field_name="section__division__branch__region", label=_("Region"), lookup_expr='exact',
                                              queryset=shared_models.Region.objects.all())
    # this is a placeholder for the filter order... real definition happens on the fly in __init__ method
    section = django_filters.ChoiceFilter(field_name="section", lookup_expr='exact',
                                          widget=forms.Select(attrs=chosen_js))
    person = django_filters.ModelChoiceFilter(field_name="resource_people2__user", label=_("Person"), lookup_expr='exact',
                                              queryset=models.User.objects.filter(resource_people__isnull=False).distinct().order_by("first_name", "last_name"),
                                              widget=forms.Select(attrs=chosen_js), )

    fgp_publication_date = django_filters.BooleanFilter(field_name="fgp_url",
                                                        lookup_expr='isnull', label=_("On FGP?"),
                                                        exclude=True,  # this will reverse the logic
                                                        )
    od_publication_date = django_filters.BooleanFilter(field_name="public_url",
                                                       lookup_expr='isnull', label=_("On Open Data Portal?"),
                                                       exclude=True,  # this will reverse the logic
                                                       )
    has_review = django_filters.BooleanFilter(field_name="reviews",
                                              lookup_expr='isnull', label=_("Has review?"),
                                              exclude=True,  # this will reverse the logic
                                              )

    flagged_4_publication = django_filters.BooleanFilter(field_name="flagged_4_publication", lookup_expr='exact')  # placeholder for ordering
    flagged_4_deletion = django_filters.BooleanFilter(field_name="flagged_4_deletion", lookup_expr='exact')  # placeholder for ordering

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        section_choices = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.all().order_by("division__branch__region", "division__branch",
                                                                        "division", "name")]

        self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=_("Section"),
                                                              lookup_expr='exact', choices=section_choices)

        # if there is a filter on section, filter the people filter accordingly
        try:
            if self.data["region"] != "":
                section_choices = [(s.id, s.full_name) for s in
                                   shared_models.Section.objects.filter(division__branch__region_id=self.data["region"]).order_by(
                                       "division__branch__region", "division__branch", "division", "name")]
                self.filters["section"] = django_filters.ChoiceFilter(field_name="section", label=_("Section"), lookup_expr='exact',
                                                                      choices=section_choices)
        except KeyError:
            pass


class PersonFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Name or email or person"), lookup_expr='icontains',
                                            widget=forms.TextInput())


class KeywordFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(label="Keyword Search Term", lookup_expr='icontains')


class CitationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(label="Citation Search Term", lookup_expr='icontains')


class DMAFilter(django_filters.FilterSet):
    class Meta:
        model = models.DMA
        fields = {
            'section__division__branch__sector__region': ['exact'],
            'title': ['icontains'],
            'data_contact': ['exact'],
            'metadata_contact': ['exact'],
            'status': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["section__division__branch__sector__region"].label = "Region"
        self.filters["data_contact"].label = _("Data steward")
        self.filters["metadata_contact"].label = _("Metadata contact")


class UserFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(label="Search any part of name", lookup_expr='icontains')
