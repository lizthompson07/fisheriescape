import django_filters
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from shared_models.models import FiscalYear, Section, Person, SubjectMatter
from . import models, utils, model_choices
from .model_choices import request_status_choices, get_process_status_choices, tor_status_choices

YES_NO_CHOICES = [(True, _("Yes")), (False, _("No")), ]
chosen_js = {"class": "chosen-select-contains"}


class UserFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Name contains"), lookup_expr='icontains',
                                            widget=forms.TextInput())


class PersonFilter(django_filters.FilterSet):
    class Meta:
        model = Person
        fields = {
            'last_name': ['exact'],
            'affiliation': ['icontains'],
            'expertise': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["last_name"] = django_filters.CharFilter(field_name='search_term', label=_("Any part of name or email"),
                                                              lookup_expr='icontains', widget=forms.TextInput())
        self.filters["expertise"].field.widget = forms.SelectMultiple(attrs=chosen_js)


class CSASRequestFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name='search', lookup_expr='icontains', label=_("Title contains OR reference number"))
    request_id = django_filters.NumberFilter(field_name='id', lookup_expr='exact')
    fiscal_year = django_filters.MultipleChoiceFilter(field_name='fiscal_year', lookup_expr='exact')
    advice_fiscal_year = django_filters.MultipleChoiceFilter(field_name='advice_fiscal_year', lookup_expr='exact')
    office = django_filters.ChoiceFilter(field_name="office", label=_("CSAS office"), lookup_expr='exact')
    region = django_filters.MultipleChoiceFilter(field_name="section__division__branch__sector__region", label=_("Client region"), lookup_expr='exact')
    sector = django_filters.MultipleChoiceFilter(field_name="section__division__branch__sector", label=_("Client sector"), lookup_expr='exact')
    section = django_filters.MultipleChoiceFilter(field_name="section", label=_("Client Section"), lookup_expr='exact')
    has_process = django_filters.BooleanFilter(field_name='processes', lookup_expr='isnull', label=_("Has process?"), exclude=True)
    status = django_filters.MultipleChoiceFilter(field_name='status', lookup_expr='exact', label=_("Status"), widget=forms.SelectMultiple(attrs=chosen_js))
    client = django_filters.ChoiceFilter(field_name="client", label=_("Client"), lookup_expr='exact')
    decision = django_filters.ChoiceFilter(field_name="review__decision", label=_("Recommendation"), lookup_expr='exact')
    prioritization = django_filters.ChoiceFilter(field_name="prioritization", label=_("Client prioritization"), lookup_expr='exact')
    tags = django_filters.MultipleChoiceFilter(field_name="tags", label=_("Keyword tags"), lookup_expr='exact', distinct=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        region_choices = utils.get_region_choices(with_requests=True)
        sector_choices = utils.get_sector_choices(with_requests=True)
        section_choices = utils.get_section_choices(with_requests=True)
        advice_fy_choices = [(fy.id, str(fy)) for fy in FiscalYear.objects.filter(csas_request_advice__isnull=False).distinct()]
        client_choices = [(u.id, str(u)) for u in User.objects.filter(csas_client_requests__isnull=False).order_by("first_name", "last_name").distinct()]
        office_choices = [(o.id, str(o)) for o in models.CSASOffice.objects.all()]
        decision_choices = model_choices.request_decision_choices
        prioritization_choices = model_choices.prioritization_choices

        fy_choices = [(fy.id, str(fy)) for fy in FiscalYear.objects.filter(csas_requests__isnull=False).distinct()]
        self.filters['fiscal_year'].field.choices = fy_choices
        self.filters['fiscal_year'].field.widget.attrs = chosen_js

        tag_choices = [(o.id, str(o)) for o in SubjectMatter.objects.filter(csasrequest__isnull=False).distinct()]
        self.filters['tags'].field.choices = tag_choices
        self.filters['tags'].field.widget.attrs = chosen_js

        self.filters['region'].field.choices = region_choices
        self.filters['sector'].field.choices = sector_choices
        self.filters['section'].field.choices = section_choices
        self.filters['client'].field.choices = client_choices
        self.filters['status'].field.choices = request_status_choices
        self.filters['advice_fiscal_year'].field.choices = advice_fy_choices
        self.filters['decision'].field.choices = decision_choices
        self.filters['prioritization'].field.choices = prioritization_choices
        self.filters['office'].field.choices = office_choices


        self.filters['client'].field.widget.attrs = chosen_js
        self.filters['advice_fiscal_year'].field.widget.attrs = chosen_js
        self.filters['section'].field.widget.attrs = chosen_js
        self.filters['region'].field.widget.attrs = chosen_js
        self.filters['sector'].field.widget.attrs = chosen_js

        regions = None
        if hasattr(self.data, "getlist"):
            regions = self.data.getlist("region")

        sectors = None
        if hasattr(self.data, "getlist"):
            sectors = self.data.getlist("sector")
        try:
            if regions and len(regions) > 0 and "" not in regions:
                sector_choices = []
                section_choices = []
                for r in regions:
                    my_region_id = int(r)
                    sector_choices.extend([my_set for my_set in utils.get_sector_choices(region_filter=my_region_id)])
                    section_choices.extend([my_set for my_set in utils.get_section_choices() if
                                            Section.objects.get(pk=my_set[0]).division.branch.region_id == my_region_id])
                self.filters['sector'].field.choices = sector_choices
                self.filters['section'].field.choices = section_choices
            if sectors and len(sectors) > 0 and "" not in sectors:
                section_choices = []
                for s in sectors:
                    my_sector_id = int(s)
                    section_choices.extend([my_set for my_set in utils.get_section_choices() if
                                            Section.objects.get(pk=my_set[0]).division.branch.sector_id == my_sector_id])
                self.filters['section'].field.choices = section_choices

        except KeyError:
            print('no data in filter')


class ProcessFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name='id', lookup_expr='exact', label=_("Process ID"))
    status = django_filters.MultipleChoiceFilter(field_name='status', lookup_expr='exact', label=_("Status"), widget=forms.SelectMultiple(attrs=chosen_js))
    fiscal_year = django_filters.MultipleChoiceFilter(field_name='fiscal_year', lookup_expr='exact')
    search = django_filters.CharFilter(field_name='search', lookup_expr='icontains', label=_("Title contains"))
    lead_office = django_filters.ChoiceFilter(field_name="lead_office", label=_("Lead Office"), lookup_expr='exact')
    csas_requests__client = django_filters.ChoiceFilter(field_name="csas_requests__client", label=_("Request client"), lookup_expr='exact')
    tor_status = django_filters.ChoiceFilter(field_name='tor__status', lookup_expr='exact', label=_("ToR status"), widget=forms.Select(attrs=chosen_js))
    sections = django_filters.MultipleChoiceFilter(field_name="csas_requests__section", label=_("Client Section"), lookup_expr='exact')
    sectors = django_filters.MultipleChoiceFilter(field_name="csas_requests__section__division__branch__sector", label=_("Client sector"), lookup_expr='exact')
    regions = django_filters.MultipleChoiceFilter(field_name="csas_requests__section__division__branch__sector__region", label=_("Client region"), lookup_expr='exact')
    tags = django_filters.MultipleChoiceFilter(field_name="csas_requests__tags", label=_("Request keyword tags"), lookup_expr='exact', distinct=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        office_choices = [(obj.id, str(obj)) for obj in models.CSASOffice.objects.all()]
        client_choices = [(u.id, str(u)) for u in User.objects.filter(csas_client_requests__isnull=False).distinct().order_by("first_name", "last_name")]
        region_choices = utils.get_region_choices(with_requests=True)
        sector_choices = utils.get_sector_choices(with_requests=True)
        section_choices = utils.get_section_choices(with_requests=True)

        fy_choices = [(fy.id, str(fy)) for fy in FiscalYear.objects.filter(processes__isnull=False).distinct()]
        self.filters['fiscal_year'].field.choices = fy_choices
        self.filters['fiscal_year'].field.widget.attrs = chosen_js

        tag_choices = [(o.id, str(o)) for o in SubjectMatter.objects.filter(csasrequest__isnull=False).distinct()]
        self.filters['tags'].field.choices = tag_choices
        self.filters['tags'].field.widget.attrs = chosen_js

        self.filters['csas_requests__client'] = django_filters.ChoiceFilter(field_name="csas_requests__client", label=_("Request client"), lookup_expr='exact',
                                                                            choices=client_choices)
        self.filters['status'].field.choices = get_process_status_choices()
        self.filters['tor_status'].field.choices = tor_status_choices
        self.filters['lead_office'].field.choices = office_choices

        self.filters['regions'].field.choices = region_choices
        self.filters['regions'].field.widget.attrs = chosen_js
        self.filters['sectors'].field.choices = sector_choices
        self.filters['sectors'].field.widget.attrs = chosen_js
        self.filters['sections'].field.choices = section_choices
        self.filters['sections'].field.widget.attrs = chosen_js

        regions = None
        if hasattr(self.data, "getlist"):
            regions = self.data.getlist("regions")

        sectors = None
        if hasattr(self.data, "getlist"):
            sectors = self.data.getlist("sectors")
        try:
            if regions and len(regions) > 0 and "" not in regions:
                sector_choices = []
                section_choices = []
                for r in regions:
                    my_region_id = int(r)
                    sector_choices.extend([my_set for my_set in utils.get_sector_choices(region_filter=my_region_id)])
                    section_choices.extend([my_set for my_set in utils.get_section_choices() if
                                            Section.objects.get(pk=my_set[0]).division.branch.region_id == my_region_id])
                self.filters['sector'].field.choices = sector_choices
                self.filters['section'].field.choices = section_choices
            if sectors and len(sectors) > 0 and "" not in sectors:
                section_choices = []
                for s in sectors:
                    my_sector_id = int(s)
                    section_choices.extend([my_set for my_set in utils.get_section_choices() if
                                            Section.objects.get(pk=my_set[0]).division.branch.sector_id == my_sector_id])
                self.filters['section'].field.choices = section_choices

        except KeyError:
            print('no data in filter')

    class Meta:
        model = models.Process
        fields = {
            'type': ['exact'],
            'status': ['exact'],
            'is_posted': ['exact'],
            'has_peer_review_meeting': ['exact'],
        }


class MeetingFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', lookup_expr='icontains', label=_("Meeting Title contains"))
    is_posted = django_filters.ChoiceFilter(field_name="process__is_posted", label=_("Is Posted?"), lookup_expr='exact', empty_label=_("All"), choices=YES_NO_CHOICES)

    class Meta:
        model = models.Meeting
        fields = {
            'process': ['exact'],
            'process__fiscal_year': ['exact'],
            'fiscal_year': ['exact'],
            'process__lead_office': ['exact'],
            'process__status': ['exact'],
            'is_planning': ['exact'],
            'is_estimate': ['exact'],

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fy_choices = [(fy.id, str(fy)) for fy in FiscalYear.objects.filter(processes__isnull=False).distinct()]
        status_choices = model_choices.get_process_status_choices()

        self.filters['process'].field.widget.attrs = chosen_js
        self.filters['process__lead_office'].label = _("Lead CSAS office")
        self.filters['is_estimate'].label = _("Are dates approximate?")
        self.filters['process__fiscal_year'] = django_filters.ChoiceFilter(field_name='process__fiscal_year', lookup_expr='exact', choices=fy_choices, label=_("Fiscal year of process"))
        self.filters['process__status'] = django_filters.MultipleChoiceFilter(field_name='process__status', lookup_expr='exact', choices=status_choices)
        self.filters['process__status'].field.widget.attrs = chosen_js


class DocumentFilter(django_filters.FilterSet):
    class Meta:
        model = models.Document
        fields = {
            'id': ['exact'],
            'document_type': ['exact'],
            'status': ['exact'],
            'translation_status': ['exact'],
            'process': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["id"] = django_filters.CharFilter(field_name='search_term', label=_("Title contains"),
                                                       lookup_expr='icontains', widget=forms.TextInput())
