from django.contrib import messages
from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy, gettext as _

from lib.templatetags.custom_filters import nz
from shared_models.views import CommonTemplateView, CommonFormView, CommonDeleteView, CommonDetailView, \
    CommonCreateView, CommonUpdateView, CommonFilterView, CommonPopoutDeleteView, CommonPopoutUpdateView, CommonPopoutCreateView
from . import models, forms, filters, utils
from .mixins import LoginAccessRequiredMixin, CsasAdminRequiredMixin, CanModifyRequestRequiredMixin, CanModifyProcessRequiredMixin
from .utils import in_csas_admin_group


class IndexTemplateView(LoginAccessRequiredMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'csas2/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_csas_admin_group(self.request.user)
        return context


# csas requests #
#################

class CSASRequestListView(LoginAccessRequiredMixin, CommonFilterView):
    template_name = 'csas2/list.html'
    filterset_class = filters.CSASRequestFilter
    paginate_by = 25
    home_url_name = "csas2:index"
    new_object_url = reverse_lazy("csas2:request_new")
    row_object_url_name = row_ = "csas2:request_detail"
    container_class = "container-fluid"

    field_list = [
        {"name": 'fiscal_year', "class": "", "width": ""},
        {"name": 'id|{}'.format("request id"), "class": "", "width": ""},
        {"name": 'tname|{}'.format("title"), "class": "", "width": ""},
        {"name": 'coordinator', "class": "", "width": ""},
        {"name": 'client', "class": "", "width": ""},
        {"name": 'section.full_name', "class": "", "width": ""},
    ]

    def get_queryset(self):
        return models.CSASRequest.objects.annotate(
            search_term=Concat('name', Value(" "), 'nom', output_field=TextField()))


class CSASRequestDetailView(LoginAccessRequiredMixin, CommonDetailView):
    model = models.CSASRequest
    template_name = 'csas2/request_detail/main.html'
    home_url_name = "csas2:index"
    parent_crumb = {"title": gettext_lazy("CSAS Requests"), "url": reverse_lazy("csas2:request_list")}

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = super().get_context_data(**kwargs)
        context["request_field_list"] = utils.get_request_field_list(obj, self.request.user)
        context["review_field_list"] = utils.get_review_field_list()
        return context


class CSASRequestCreateView(LoginAccessRequiredMixin, CommonCreateView):
    model = models.CSASRequest
    form_class = forms.CSASRequestForm
    template_name = 'csas2/request_form.html'
    home_url_name = "csas2:index"
    parent_crumb = {"title": gettext_lazy("CSAS Requests"), "url": reverse_lazy("csas2:request_list")}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super().form_valid(form)


class CSASRequestUpdateView(CanModifyRequestRequiredMixin, CommonUpdateView):
    model = models.CSASRequest
    form_class = forms.CSASRequestForm
    template_name = 'csas2/request_form.html'
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("CSAS Requests"), "url": reverse_lazy("csas2:request_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:request_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class CSASRequestDeleteView(CanModifyRequestRequiredMixin, CommonDeleteView):
    model = models.CSASRequest
    success_url = reverse_lazy('csas2:request_list')
    template_name = 'csas2/confirm_delete.html'
    delete_protection = False
    grandparent_crumb = {"title": gettext_lazy("CSAS Requests"), "url": reverse_lazy("csas2:request_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:request_detail", args=[self.get_object().id])}


class CSASRequestSubmitView(CSASRequestUpdateView):
    template_name = 'csas2/request_submit.html'
    form_class = forms.TripRequestTimestampUpdateForm
    submit_text = gettext_lazy("Proceed")

    def get_active_page_name_crumb(self):
        my_object = self.get_object()
        return _("Un-submit request") if my_object.submission_date else _("Submit request")

    def get_h1(self):
        my_object = self.get_object()
        if my_object.submission_date:
            return _("Do you wish to un-submit the following request?")
        else:
            return _("Do you wish to submit the following request?")

    def get_h3(self):
        my_object = self.get_object()
        if not my_object.submission_date:
            return _("Please ensure the following items have been completed:")

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:request_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        if obj.submission_date:
            obj.submission_date = None
        else:
            obj.submission_date = timezone.now()
        return super().form_valid(form)


# csas requests #
#################


class CSASRequestReviewCreateView(CanModifyRequestRequiredMixin, CommonCreateView):
    model = models.CSASRequestReview
    form_class = forms.CSASRequestReviewForm
    template_name = 'csas2/form.html'
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("CSAS Requests"), "url": reverse_lazy("csas2:request_list")}
    submit_text = gettext_lazy("Start a Review")

    def get_csas_request(self):
        return get_object_or_404(models.CSASRequest, pk=self.kwargs.get("crequest"))

    def get_parent_crumb(self):
        return {"title": self.get_csas_request(), "url": reverse_lazy("csas2:request_detail", args=[self.get_csas_request().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.csas_request = self.get_csas_request()
        obj.created_by = self.request.user
        return super().form_valid(form)


class CSASRequestReviewUpdateView(CanModifyRequestRequiredMixin, CommonUpdateView):
    model = models.CSASRequestReview
    form_class = forms.CSASRequestReviewForm
    template_name = 'csas2/form.html'
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("CSAS Requests"), "url": reverse_lazy("csas2:request_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object().csas_request, "url": reverse_lazy("csas2:request_detail", args=[self.get_object().csas_request.id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class CSASRequestReviewDeleteView(CanModifyRequestRequiredMixin, CommonDeleteView):
    model = models.CSASRequestReview
    template_name = 'csas2/confirm_delete.html'
    delete_protection = False
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("CSAS Requests"), "url": reverse_lazy("csas2:request_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object().csas_request, "url": reverse_lazy("csas2:request_detail", args=[self.get_object().csas_request.id])}

    def delete(self, request, *args, **kwargs):
        # a little bit of gymnastics here in order to save the csas request truely following the deletion of the review (not working with signals)
        obj = self.get_object()
        csas_request = obj.csas_request
        success_url = self.get_parent_crumb().get("url")
        obj.delete()
        csas_request.save()
        return HttpResponseRedirect(success_url)



# request files #
#################

class CSASRequestFileCreateView(CanModifyRequestRequiredMixin, CommonPopoutCreateView):
    model = models.CSASRequestFile
    form_class = forms.CSASRequestFileForm
    is_multipart_form_data = True

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.csas_request_id = self.kwargs['crequest']
        obj.save()
        return HttpResponseRedirect(self.get_success_url())


class CSASRequestFileUpdateView(CanModifyRequestRequiredMixin, CommonPopoutUpdateView):
    model = models.CSASRequestFile
    form_class = forms.CSASRequestFileForm
    is_multipart_form_data = True


class CSASRequestFileDeleteView(CanModifyRequestRequiredMixin, CommonPopoutDeleteView):
    model = models.CSASRequestFile


# processes #
#################

class ProcessListView(LoginAccessRequiredMixin, CommonFilterView):
    template_name = 'csas2/list.html'
    filterset_class = filters.ProcessFilter
    paginate_by = 25
    home_url_name = "csas2:index"
    new_object_url = reverse_lazy("csas2:process_new")
    row_object_url_name = row_ = "csas2:process_detail"
    container_class = "container-fluid"

    field_list = [
        {"name": 'fiscal_year', "class": "", "width": ""},
        {"name": 'id|{}'.format("request id"), "class": "", "width": ""},
        {"name": 'tname|{}'.format("title"), "class": "", "width": ""},
        {"name": 'coordinator', "class": "", "width": ""},
        {"name": 'client', "class": "", "width": ""},
    ]

    def get_queryset(self):
        return models.Process.objects.annotate(
            search_term=Concat('name', Value(" "), 'nom', output_field=TextField()))


class ProcessDetailView(LoginAccessRequiredMixin, CommonDetailView):
    model = models.Process
    template_name = 'csas2/process_detail/main.html'
    home_url_name = "csas2:index"
    parent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = super().get_context_data(**kwargs)
        context["process_field_list"] = utils.get_process_field_list()
        return context


class ProcessCreateView(CsasAdminRequiredMixin, CommonCreateView):
    model = models.Process
    form_class = forms.ProcessForm
    template_name = 'csas2/form.html'
    home_url_name = "csas2:index"
    parent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_initial(self):
        qp = self.request.GET
        if qp.get("request"):
            return dict(csas_requests=[qp.get("request"), ])

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super().form_valid(form)


class ProcessUpdateView(CanModifyProcessRequiredMixin, CommonUpdateView):
    model = models.Process
    form_class = forms.ProcessForm
    template_name = 'csas2/process_form.html'
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:process_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class ProcessDeleteView(CanModifyProcessRequiredMixin, CommonDeleteView):
    model = models.Process
    success_url = reverse_lazy('csas2:process_list')
    template_name = 'csas2/confirm_delete.html'
    delete_protection = False
    grandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:process_detail", args=[self.get_object().id])}


# REPORTS #
###########

class ReportSearchFormView(CsasAdminRequiredMixin, CommonFormView):
    template_name = 'csas2/report_search.html'
    form_class = forms.ReportSearchForm
    h1 = gettext_lazy("eDNA Reports")

    def form_valid(self, form):
        report = int(form.cleaned_data["report"])
        year = nz(form.cleaned_data["year"], "None")
        messages.error(self.request, "Report is not available. Please select another report.")
        return HttpResponseRedirect(reverse("csas2:reports"))
