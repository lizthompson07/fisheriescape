from datetime import datetime

from django.contrib import messages
from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy, gettext as _

from lib.templatetags.custom_filters import nz
from shared_models.models import Person
from shared_models.views import CommonTemplateView, CommonFormView, CommonDeleteView, CommonDetailView, \
    CommonCreateView, CommonUpdateView, CommonFilterView, CommonPopoutDeleteView, CommonPopoutUpdateView, CommonPopoutCreateView, CommonFormsetView, \
    CommonHardDeleteView
from . import models, forms, filters, utils
from .mixins import LoginAccessRequiredMixin, CsasAdminRequiredMixin, CanModifyRequestRequiredMixin, CanModifyProcessRequiredMixin, \
    CsasNationalAdminRequiredMixin
from .utils import in_csas_admin_group


class IndexTemplateView(LoginAccessRequiredMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'csas2/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_csas_admin_group(self.request.user)
        return context


# settings
##########

class SeriesFormsetView(CsasNationalAdminRequiredMixin, CommonFormsetView):
    template_name = 'csas2/formset.html'
    h1 = "Manage Publication Series"
    queryset = models.Series.objects.all()
    formset_class = forms.SeriesFormset
    success_url_name = "csas2:manage_series"
    home_url_name = "csas2:index"
    delete_url_name = "csas2:delete_series"


class SeriesHardDeleteView(CsasNationalAdminRequiredMixin, CommonHardDeleteView):
    model = models.Series
    success_url = reverse_lazy("csas2:manage_series")


# people #
##########

class PersonListView(CsasAdminRequiredMixin, CommonFilterView):
    template_name = 'csas2/list.html'
    filterset_class = filters.PersonFilter
    model = Person
    queryset = Person.objects.annotate(
        search_term=Concat('first_name',
                           Value(" "),
                           'last_name',
                           Value(" "),
                           'email', output_field=TextField()))
    field_list = [
        {"name": 'full_name|{}'.format(gettext_lazy("name")), "class": "", "width": ""},
        {"name": 'phone', "class": "", "width": ""},
        {"name": 'email', "class": "", "width": ""},
        {"name": 'affiliation', "class": "", "width": ""},
        {"name": 'has_linked_user|{}'.format(_("Linked to DM Apps user?")), "class": "", "width": ""},
    ]
    new_object_url_name = "csas2:person_new"
    row_object_url_name = "csas2:person_detail"
    home_url_name = "csas2:index"
    paginate_by = 25
    h1 = gettext_lazy("Contacts")


class PersonDetailView(CsasAdminRequiredMixin, CommonDetailView):
    model = Person
    template_name = 'csas2/person_detail.html'
    field_list = utils.get_person_field_list()
    home_url_name = "csas2:index"
    parent_crumb = {"title": gettext_lazy("Contacts"), "url": reverse_lazy("csas2:person_list")}


class PersonUpdateView(CsasAdminRequiredMixin, CommonUpdateView):
    model = Person
    template_name = 'csas2/form.html'
    form_class = forms.PersonForm
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("Contacts"), "url": reverse_lazy("csas2:person_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("csas2:person_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.upated_by = self.request.user
        obj.save()
        return super().form_valid(form)


class PersonCreateView(CsasAdminRequiredMixin, CommonCreateView):
    model = Person
    template_name = 'csas2/form.html'
    form_class = forms.PersonForm
    home_url_name = "csas2:index"
    parent_crumb = {"title": gettext_lazy("Contacts"), "url": reverse_lazy("csas2:person_list")}
    h1 = gettext_lazy("New Contact")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.save()
        return super().form_valid(form)


class PersonDeleteView(CsasAdminRequiredMixin, CommonDeleteView):
    model = Person
    template_name = 'csas2/confirm_delete.html'
    success_url = reverse_lazy('csas2:person_list')
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("Contacts"), "url": reverse_lazy("csas2:person_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("csas2:person_detail", args=[self.get_object().id])}


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
        {"name": 'id', "class": "", "width": "50px"},
        {"name": 'fiscal_year', "class": "", "width": "100px"},
        {"name": 'ref_number|{}'.format(_("reference number")), "class": "", "width": "150px"},
        {"name": 'title|{}'.format("title"), "class": "", "width": ""},
        {"name": 'status', "class": "", "width": "100px"},
        {"name": 'coordinator', "class": "", "width": "150px"},
        {"name": 'section.full_name|{}'.format(_("Region/Sector")), "class": "", "width": "30%"},
    ]

    def get_queryset(self):
        qp = self.request.GET
        qs = models.CSASRequest.objects.all()
        if qp.get("personalized"):
            qs = utils.get_related_requests(self.request.user)
        qs = qs.annotate(search_term=Concat('title', Value(" "), 'translated_title', Value(" "), 'reference_number', output_field=TextField()))
        return qs

    def get_h1(self):
        qp = self.request.GET
        if qp.get("personalized"):
            return _("My CSAS Requests")
        return _("CSAS Requests")


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


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_csas_admin_group(self.request.user)
        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_csas_admin_group(self.request.user)
        return context

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


# csas request reviews #
########################


class CSASRequestReviewCreateView(CanModifyRequestRequiredMixin, CommonCreateView):
    model = models.CSASRequestReview
    form_class = forms.CSASRequestReviewForm
    template_name = 'csas2/request_form.html' #  shared js_body
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
    template_name = 'csas2/request_form.html'  #  shared js_body
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
        {"name": 'id', "class": "", "width": ""},
        {"name": 'fiscal_year', "class": "", "width": ""},
        {"name": 'tname|{}'.format("title"), "class": "", "width": ""},
        {"name": 'status', "class": "", "width": ""},
        {"name": 'scope_type|{}'.format(_("advisory type")), "class": "", "width": ""},
        {"name": 'lead_region', "class": "", "width": ""},
        {"name": 'other_regions', "class": "", "width": ""},
        {"name": 'coordinator', "class": "", "width": ""},
        {"name": 'advisors|{}'.format(_("science advisors")), "class": "", "width": ""},
    ]

    def get_queryset(self):
        qp = self.request.GET
        qs = models.Process.objects.all()
        if qp.get("personalized"):
            qs = utils.get_related_processes(self.request.user)
        qs = qs.annotate(search_term=Concat('name', Value(" "), 'nom', output_field=TextField()))
        return qs

    def get_h1(self):
        qp = self.request.GET
        if qp.get("personalized"):
            return _("My CSAS Processes")
        return _("CSAS Processes")


class ProcessDetailView(LoginAccessRequiredMixin, CommonDetailView):
    model = models.Process
    template_name = 'csas2/process_detail/main.html'
    home_url_name = "csas2:index"
    parent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = super().get_context_data(**kwargs)
        context["process_field_list"] = utils.get_process_field_list(obj)
        context["meeting_field_list"] = [
            'type',
            'location',
            'display_dates|{}'.format(_("dates")),
        ]
        context["document_field_list"] = [
            'ttitle|{}'.format(_("title")),
            'type',
            'status',
        ]
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
            csas_request = get_object_or_404(models.CSASRequest, pk=qp.get("request"))
            return dict(
                csas_requests=[csas_request.id, ],
                coordinator=csas_request.coordinator,
            )

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super().form_valid(form)


class ProcessUpdateView(CanModifyProcessRequiredMixin, CommonUpdateView):
    model = models.Process
    form_class = forms.ProcessForm
    template_name = 'csas2/form.html'
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


# meetings #
############

class MeetingListView(LoginAccessRequiredMixin, CommonFilterView):
    template_name = 'csas2/list.html'
    filterset_class = filters.MeetingFilter
    paginate_by = 25
    home_url_name = "csas2:index"
    row_object_url_name = row_ = "csas2:meeting_detail"
    container_class = "container-fluid"

    field_list = [
        {"name": 'process', "class": "", "width": ""},
        {"name": 'type', "class": "", "width": ""},
        {"name": 'tname|{}'.format("title"), "class": "", "width": ""},
        {"name": 'coordinator', "class": "", "width": ""},
        {"name": 'client', "class": "", "width": ""},
        {"name": 'section.full_name', "class": "", "width": ""},
    ]

    def get_queryset(self):
        return models.Meeting.objects.filter(hide_from_list=False).annotate(
            search_term=Concat('name', Value(" "), 'nom', output_field=TextField()))


class MeetingDetailView(LoginAccessRequiredMixin, CommonDetailView):
    model = models.Meeting
    template_name = 'csas2/meeting_detail/main.html'
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object().process, "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = super().get_context_data(**kwargs)
        context["meeting_field_list"] = utils.get_meeting_field_list()
        return context


class MeetingCreateView(CanModifyProcessRequiredMixin, CommonCreateView):
    model = models.Meeting
    form_class = forms.MeetingForm
    template_name = 'csas2/request_form.html'
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_parent_crumb(self):
        return {"title": self.get_process(), "url": reverse_lazy("csas2:process_detail", args=[self.get_process().id])}

    def get_process(self):
        return get_object_or_404(models.Process, pk=self.kwargs.get("process"))

    def form_valid(self, form):
        obj = form.save(commit=False)
        range = form.cleaned_data["date_range"].split("to")
        start_date = datetime.strptime(range[0].strip(), "%Y-%m-%d")
        obj.start_date = start_date
        if len(range) > 1:
            end_date = datetime.strptime(range[1].strip(), "%Y-%m-%d")
            obj.end_date = end_date
        else:
            obj.end_date = start_date
        obj.created_by = self.request.user
        obj.process = self.get_process()
        return super().form_valid(form)


class MeetingUpdateView(CanModifyProcessRequiredMixin, CommonUpdateView):
    model = models.Meeting
    form_class = forms.MeetingForm
    template_name = 'csas2/request_form.html'
    home_url_name = "csas2:index"
    greatgrandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_initial(self):
        obj = self.get_object()
        return dict(date_range=f"{obj.start_date.strftime('%Y-%m-%d')} to {obj.end_date.strftime('%Y-%m-%d')}")

    def get_grandparent_crumb(self):
        return {"title": self.get_object().process, "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:meeting_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        range = form.cleaned_data["date_range"].split("to")
        start_date = datetime.strptime(range[0].strip(), "%Y-%m-%d")
        obj.start_date = start_date
        if len(range) > 1:
            end_date = datetime.strptime(range[1].strip(), "%Y-%m-%d")
            obj.end_date = end_date
        else:
            obj.end_date = start_date

        obj.updated_by = self.request.user
        return super().form_valid(form)


class MeetingDeleteView(CanModifyProcessRequiredMixin, CommonDeleteView):
    model = models.Meeting
    template_name = 'csas2/confirm_delete.html'
    delete_protection = False
    greatgrandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().process, "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:meeting_detail", args=[self.get_object().id])}

    def get_success_url(self):
        return self.get_grandparent_crumb()["url"]


# documents #
############

class DocumentListView(LoginAccessRequiredMixin, CommonFilterView):
    template_name = 'csas2/list.html'
    filterset_class = filters.DocumentFilter
    paginate_by = 25
    home_url_name = "csas2:index"
    row_object_url_name = row_ = "csas2:document_detail"
    container_class = "container-fluid"

    field_list = [
        {"name": 'ttitle|{}'.format("title"), "class": "", "width": ""},
        {"name": 'type', "class": "", "width": ""},
        {"name": 'status', "class": "", "width": ""},
        {"name": 'process', "class": "", "width": ""},
        {"name": 'series', "class": "", "width": ""},
    ]

    def get_queryset(self):
        qp = self.request.GET
        qs = models.Document.objects.all()
        if qp.get("personalized"):
            qs = utils.get_related_docs(self.request.user)
        qs = qs.annotate(search_term=Concat(
            'title_en',
            Value(" "),
            'title_fr',
            output_field=TextField())
        )
        return qs

    def get_h1(self):
        qp = self.request.GET
        if qp.get("personalized"):
            return _("My Docs")
        return _("Documents")


class DocumentDetailView(LoginAccessRequiredMixin, CommonDetailView):
    model = models.Document
    template_name = 'csas2/document_detail/main.html'
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object().process, "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = super().get_context_data(**kwargs)
        return context


class DocumentCreateView(CanModifyProcessRequiredMixin, CommonCreateView):
    model = models.Document
    form_class = forms.DocumentForm
    template_name = 'csas2/request_form.html'
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_parent_crumb(self):
        return {"title": self.get_process(), "url": reverse_lazy("csas2:process_detail", args=[self.get_process().id])}

    def get_process(self):
        return get_object_or_404(models.Process, pk=self.kwargs.get("process"))

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.process = self.get_process()
        return super().form_valid(form)


class DocumentUpdateView(CanModifyProcessRequiredMixin, CommonUpdateView):
    model = models.Document
    form_class = forms.DocumentForm
    template_name = 'csas2/request_form.html'
    home_url_name = "csas2:index"
    greatgrandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().process, "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:document_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class DocumentDeleteView(CanModifyProcessRequiredMixin, CommonDeleteView):
    model = models.Document
    success_url = reverse_lazy('csas2:document_list')
    template_name = 'csas2/confirm_delete.html'
    delete_protection = False
    grandparent_crumb = {"title": gettext_lazy("CSAS Requests"), "url": reverse_lazy("csas2:document_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:document_detail", args=[self.get_object().id])}


# reports #
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
