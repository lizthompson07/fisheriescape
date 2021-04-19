from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from grais import filters
from grais import forms
from grais import models
from grais.mixins import GraisAccessRequiredMixin, GraisCRUDRequiredMixin
from shared_models.views import CommonFilterView, CommonUpdateView, CommonCreateView, \
    CommonDetailView, CommonDeleteView, CommonPopoutCreateView, CommonPopoutUpdateView, CommonPopoutDeleteView


# INCIDENTAL REPORT #
#####################

class ReportListView(GraisAccessRequiredMixin, CommonFilterView):
    model = models.IncidentalReport
    filterset_class = filters.ReportFilter
    paginate_by = 50
    template_name = "grais/list.html"
    home_url_name = "grais:index"
    row_object_url_name = "grais:ir_detail"
    new_object_url_name = "grais:ir_new"
    field_list = [
        {"name": 'season', "class": "", "width": ""},
        {"name": 'report_source', "class": "", "width": ""},
        {"name": 'requestor', "class": "", "width": ""},
        {"name": 'report_date', "class": "", "width": ""},
        {"name": 'species_list|species', "class": "", "width": ""},
        {"name": 'coordinates', "class": "", "width": ""},
        {"name": 'followup_count|follow-ups', "class": "", "width": ""},
    ]


class ReportUpdateView(GraisAccessRequiredMixin, CommonUpdateView):
    model = models.IncidentalReport
    form_class = forms.ReportForm
    template_name = "grais/form.html"
    home_url_name = "grais:index"
    grandparent_crumb = {"title": _("Reports"), "url": reverse_lazy("grais:ir_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("grais:ir_detail", args=[self.get_object().id])}


class ReportCreateView(GraisAccessRequiredMixin, CommonCreateView):
    model = models.IncidentalReport
    form_class = forms.ReportForm
    template_name = "grais/form.html"
    home_url_name = "grais:index"
    parent_crumb = {"title": _("Reports"), "url": reverse_lazy("grais:ir_list")}

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class ReportDetailView(GraisAccessRequiredMixin, CommonDetailView):
    model = models.IncidentalReport
    container_class = "container-fluid"
    template_name = "grais/incidental_reports/report_detail.html"
    home_url_name = "grais:index"
    parent_crumb = {"title": _("Reports"), "url": reverse_lazy("grais:ir_list")}
    field_list = [
        'report_date',
        'language_of_report',
        'requestor_information|requestor information',
        'coordinates',
        'report_source',
        'species_confirmation',
        'gulf_ais_confirmed',
        'seeking_general_info_ais',
        'seeking_general_info_non_ais',
        'management_related',
        'dfo_it_related',
        'incorrect_region',
        'call_answered_by',
        'call_returned_by',
        'location_description',
        'specimens_retained',
        'sighting_description',
        'identified_by',
        'date_of_occurrence',
        'observation_type',
        'notes',
        'season',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mapbox_api_key"] = settings.MAPBOX_API_KEY
        return context


class ReportDeleteView(GraisAccessRequiredMixin, CommonDeleteView):
    model = models.IncidentalReport
    template_name = "grais/confirm_delete.html"
    home_url_name = "grais:index"
    grandparent_crumb = {"title": _("Reports"), "url": reverse_lazy("grais:ir_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("grais:ir_detail", args=[self.get_object().id])}


# FOLLOW UPs #
###############

class FollowUpUpdateView(GraisCRUDRequiredMixin, CommonPopoutUpdateView):
    model = models.FollowUp
    form_class = forms.FollowUpForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()
        return super().form_valid(form)


class FollowUpCreateView(GraisCRUDRequiredMixin, CommonPopoutCreateView):
    model = models.FollowUp
    form_class = forms.FollowUpForm

    def get_initial(self):
        return dict(author=self.request.user)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.incidental_report = get_object_or_404(models.IncidentalReport, pk=self.kwargs.get("report"))
        obj.created_by = self.request.user
        obj.save()
        return super().form_valid(form)


class FollowUpDeleteView(GraisCRUDRequiredMixin, CommonPopoutDeleteView):
    model = models.FollowUp
