import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.timezone import make_aware, utc
from django.utils.translation import gettext_lazy, gettext as _

from lib.functions.custom_functions import fiscal_year
from shared_models.models import Person, FiscalYear
from shared_models.views import CommonTemplateView, CommonFormView, CommonDeleteView, CommonDetailView, \
    CommonCreateView, CommonUpdateView, CommonFilterView, CommonPopoutDeleteView, CommonPopoutUpdateView, CommonPopoutCreateView, CommonFormsetView, \
    CommonHardDeleteView
from . import models, forms, filters, utils, reports, emails
from .mixins import LoginAccessRequiredMixin, CsasAdminRequiredMixin, CanModifyRequestRequiredMixin, CanModifyProcessRequiredMixin, \
    CsasNationalAdminRequiredMixin
from .utils import in_csas_admin_group, get_quarter


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

class DocumentTypeFormsetView(CsasNationalAdminRequiredMixin, CommonFormsetView):
    template_name = 'csas2/formset.html'
    h1 = "Manage Document Type"
    queryset = models.DocumentType.objects.all()
    formset_class = forms.DocumentTypeFormset
    success_url_name = "csas2:manage_document_types"
    home_url_name = "csas2:index"
    delete_url_name = "csas2:delete_document_type"


class DocumentTypeHardDeleteView(CsasNationalAdminRequiredMixin, CommonHardDeleteView):
    model = models.DocumentType
    success_url = reverse_lazy("csas2:manage_document_types")


class InviteeRoleFormsetView(CsasNationalAdminRequiredMixin, CommonFormsetView):
    template_name = 'csas2/formset.html'
    h1 = "Manage Invitee Roles"
    queryset = models.InviteeRole.objects.all()
    formset_class = forms.InviteeRoleFormset
    success_url_name = "csas2:manage_invitee_roles"
    home_url_name = "csas2:index"
    delete_url_name = "csas2:delete_invitee_role"


class InviteeRoleHardDeleteView(CsasNationalAdminRequiredMixin, CommonHardDeleteView):
    model = models.InviteeRole
    success_url = reverse_lazy("csas2:manage_invitee_roles")


# user permissions
class UserListView(CsasNationalAdminRequiredMixin, CommonFilterView):
    template_name = "csas2/user_list.html"
    filterset_class = filters.UserFilter
    home_url_name = "index"
    paginate_by = 25
    h1 = "CSAS Tracking Tool User Permissions"
    field_list = [
        {"name": 'first_name', "class": "", "width": ""},
        {"name": 'last_name', "class": "", "width": ""},
        {"name": 'email', "class": "", "width": ""},
        {"name": 'last_login|{}'.format(gettext_lazy("Last login to DM Apps")), "class": "", "width": ""},
    ]
    new_object_url = reverse_lazy("shared_models:user_new")

    def get_queryset(self):
        queryset = User.objects.order_by("first_name", "last_name").annotate(
            search_term=Concat('first_name', Value(""), 'last_name', Value(""), 'email', output_field=TextField())
        )
        if self.request.GET.get("csas_only"):
            nat_group, created = Group.objects.get_or_create(name="csas_national_admin")
            reg_group, created = Group.objects.get_or_create(name="csas_regional_admin")
            queryset = queryset.filter(groups__in=[nat_group, reg_group]).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nat_group, created = Group.objects.get_or_create(name="csas_national_admin")
        reg_group, created = Group.objects.get_or_create(name="csas_regional_admin")
        context["nat_group"] = Group.objects.get(name="projects_admin")
        return context


# @login_required(login_url='/accounts/login/')
# @user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
# def toggle_user(request, pk, type):
#     if in_projects_admin_group(request.user):
#         my_user = User.objects.get(pk=pk)
#         admin_group = Group.objects.get(name="projects_admin")
#         if type == "admin":
#             # if the user is in the admin group, remove them
#             if admin_group in my_user.groups.all():
#                 my_user.groups.remove(admin_group)
#             # otherwise add them
#             else:
#                 my_user.groups.add(admin_group)
#         return HttpResponseRedirect("{}#user_{}".format(request.META.get('HTTP_REFERER'), my_user.id))
#     else:
#         return HttpResponseForbidden("sorry, not authorized")



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
        {"name": 'ref_number', "class": "", "width": "150px"},
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
        qs = qs.annotate(search_term=Concat('title', Value(" "), 'translated_title', Value(" "), 'ref_number', output_field=TextField()))
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
    container_class = ""

    def get_active_page_name_crumb(self):
        return "{} {}".format(_("Request"), self.get_object().id)

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = super().get_context_data(**kwargs)
        context["request_field_list"] = utils.get_request_field_list(obj, self.request.user)
        context["review_field_list"] = utils.get_review_field_list()
        return context


class CSASRequestCreateView(LoginAccessRequiredMixin, CommonCreateView):
    model = models.CSASRequest
    form_class = forms.CSASRequestForm
    template_name = 'csas2/js_form.html'
    home_url_name = "csas2:index"
    parent_crumb = {"title": gettext_lazy("CSAS Requests"), "url": reverse_lazy("csas2:request_list")}
    submit_text = gettext_lazy("Save")

    def get_initial(self):
        return dict(
            client=self.request.user
        )

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
    template_name = 'csas2/js_form.html'
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("CSAS Requests"), "url": reverse_lazy("csas2:request_list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_csas_admin_group(self.request.user)
        return context

    def get_parent_crumb(self):
        return {"title": "{} {}".format(_("Request"), self.get_object().id), "url": reverse_lazy("csas2:request_detail", args=[self.get_object().id])}

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
        return {"title": "{} {}".format(_("Request"), self.get_object().id), "url": reverse_lazy("csas2:request_detail", args=[self.get_object().id])}


class CSASRequestSubmitView(CSASRequestUpdateView):
    template_name = 'csas2/request_submit.html'
    form_class = forms.TripRequestTimestampUpdateForm
    submit_text = gettext_lazy("Proceed")

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
        return {"title": "{} {}".format(_("Request"), self.get_object().id), "url": reverse_lazy("csas2:request_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        if obj.submission_date:
            obj.submission_date = None
        else:
            obj.submission_date = timezone.now()
        obj.save()

        # if the request was just submitted, send an email
        if obj.submission_date:
            email = emails.NewRequestEmail(self.request, obj)
            email.send()
        return HttpResponseRedirect(self.get_success_url())


class CSASRequestCloneUpdateView(CSASRequestUpdateView):
    h1 = gettext_lazy("Clone a CSAS Request")
    h2 = gettext_lazy("Please update the request details")

    def test_func(self):
        if self.request.user.id:
            return True

    def get_initial(self):
        my_object = models.CSASRequest.objects.get(pk=self.kwargs["pk"])
        data = dict(
            title=f"COPY OF: {my_object.title}",
            client=self.request.user,
            advice_needed_by=None,
        )
        return data

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        new_obj.pk = None
        new_obj.status = 1
        new_obj.submission_date = None
        new_obj.old_id = None
        new_obj.uuid = None
        new_obj.ref_number = None
        new_obj.created_by = self.request.user
        new_obj.notes = None
        new_obj.save()
        return HttpResponseRedirect(reverse_lazy("csas2:request_detail", args=[new_obj.id]))


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
        {"name": 'tname|{}'.format("title"), "class": "", "width": "300px"},
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

    def get_active_page_name_crumb(self):
        return "{} {}".format(_("Process"), self.get_object().id)

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = super().get_context_data(**kwargs)
        context["process_field_list"] = utils.get_process_field_list(obj)
        context["meeting_field_list"] = [
            'display|{}'.format(_("title")),
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
    submit_text = gettext_lazy("Save")

    def get_initial(self):
        data = dict(
            fiscal_year=fiscal_year(timezone.now(), sap_style=True),
        )
        qp = self.request.GET
        if qp.get("request"):
            csas_request = get_object_or_404(models.CSASRequest, pk=qp.get("request"))
            data["name"] = csas_request.title
            data["csas_requests"] = [csas_request.id, ]
            data["coordinator"] = csas_request.coordinator
        return data

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
        return {"title": "{} {}".format(_("Process"), self.get_object().id), "url": reverse_lazy("csas2:process_detail", args=[self.get_object().id])}

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
        return {"title": "{} {}".format(_("Process"), self.get_object().id), "url": reverse_lazy("csas2:process_detail", args=[self.get_object().id])}


class ProcessPostingsVueJSView(CsasNationalAdminRequiredMixin, CommonFilterView):  # using the common filter view to bring in the django filter machinery
    template_name = 'csas2/process_postings.html'
    home_url_name = "csas2:index"
    container_class = "container-fluid"
    h1 = gettext_lazy("Manage Process Postings")
    model = models.Process
    filterset_class = filters.ProcessFilter


# ToR #
#######

class TermsOfReferenceCreateView(CanModifyProcessRequiredMixin, CommonCreateView):
    model = models.TermsOfReference
    form_class = forms.TermsOfReferenceForm
    template_name = 'csas2/tor_form.html'
    home_url_name = "csas2:index"
    submit_text = gettext_lazy("Initiate ToR")
    grandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_initial(self):
        """ For the benefit of the form class"""
        return dict(
            process=self.kwargs.get("process"),
        )

    def get_parent_crumb(self):
        return {"title": "{} {}".format(_("Process"), self.get_process().id), "url": reverse_lazy("csas2:process_detail", args=[self.get_process().id])}

    def get_process(self):
        return get_object_or_404(models.Process, pk=self.kwargs.get("process"))

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.process = self.get_process()
        obj.created_by = self.request.user
        return super().form_valid(form)


class TermsOfReferenceUpdateView(CanModifyProcessRequiredMixin, CommonUpdateView):
    model = models.TermsOfReference
    form_class = forms.TermsOfReferenceForm
    template_name = 'csas2/tor_form.html'  # shared js_body
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_parent_crumb(self):
        return {"title": "{} {}".format(_("Process"), self.get_object().process.id),
                "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user

        old_obj = models.TermsOfReference.objects.get(pk=obj.id)
        obj.save()
        print(123)
        # now for the piece about NCR email
        if obj.process.is_posted and \
                (old_obj.expected_publications_en != obj.expected_publications_en or old_obj.expected_publications_fr != obj.expected_publications_fr):
            if not obj.meeting:
                messages.error(self.request, "tried to send an email to NCR but this TOR has no meeting!")
            else:
                email = emails.UpdatedMeetingEmail(self.request, obj.meeting, obj.process.tor)
                email.send()
        return HttpResponseRedirect(self.get_success_url())


class TermsOfReferenceDeleteView(CanModifyProcessRequiredMixin, CommonDeleteView):
    model = models.TermsOfReference
    template_name = 'csas2/confirm_delete.html'
    delete_protection = False
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_parent_crumb(self):
        return {"title": "{} {}".format(_("Process"), self.get_object().process.id),
                "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

    def get_success_url(self):
        return self.get_parent_crumb().get("url")


@login_required()
def tor_export(request, pk):
    tor = get_object_or_404(models.TermsOfReference, pk=pk)

    qp = request.GET
    lang = qp.get("lang", "en")  # default to english if no query

    file_url = reports.generate_tor(tor, lang)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-word")
            if lang == "fr":
                filename = f'CdeR (no. projet {tor.process.id}).docx'
            else:
                filename = f'ToR (Process ID {tor.process.id}).docx'

            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
    raise Http404


class TermsOfReferenceHTMLDetailView(LoginAccessRequiredMixin, CommonDetailView):
    model = models.TermsOfReference

    def get_template_names(self, **kwargs):
        qp = self.request.GET
        lang = qp.get("lang", "en")  # default to english if no query
        return 'csas2/tor_html_fr.html' if lang == "fr" else 'csas2/tor_html_en.html'


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
        return {"title": "{} {}".format(_("Process"), self.get_object().process.id),
                "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = super().get_context_data(**kwargs)
        context["meeting_field_list"] = utils.get_meeting_field_list()
        return context


class MeetingCreateView(CanModifyProcessRequiredMixin, CommonCreateView):
    model = models.Meeting
    form_class = forms.MeetingForm
    template_name = 'csas2/js_form.html'
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_initial(self):
        return dict(est_year=timezone.now().year, est_quarter=get_quarter(timezone.now()))

    def get_parent_crumb(self):
        return {"title": "{} {}".format(_("Process"), self.get_process().id), "url": reverse_lazy("csas2:process_detail", args=[self.get_process().id])}

    def get_process(self):
        return get_object_or_404(models.Process, pk=self.kwargs.get("process"))

    def form_valid(self, form):
        obj = form.save(commit=False)
        range = form.cleaned_data["date_range"]
        if range:
            range = range.split("to")
            start_date = datetime.strptime(range[0].strip(), "%Y-%m-%d")
            obj.start_date = start_date
            if len(range) > 1:
                end_date = datetime.strptime(range[1].strip(), "%Y-%m-%d")
                obj.end_date = end_date
            else:
                obj.end_date = start_date
        obj.created_by = self.request.user
        obj.process = self.get_process()

        obj.save()

        # now for the piece about NCR email
        if obj.process.is_posted and not obj.is_planning:
            if not hasattr(obj.process, "tor"):
                messages.error(self.request, "tried to send an email to NCR but this process has no TOR!")
            else:
                email = emails.UpdatedMeetingEmail(self.request, obj, obj.process.tor)
                email.send()
        return HttpResponseRedirect(self.get_success_url())



class MeetingUpdateView(CanModifyProcessRequiredMixin, CommonUpdateView):
    model = models.Meeting
    form_class = forms.MeetingForm
    template_name = 'csas2/js_form.html'
    home_url_name = "csas2:index"
    greatgrandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_initial(self):
        obj = self.get_object()
        if obj.start_date:
            return dict(date_range=f"{obj.start_date.strftime('%Y-%m-%d')} to {obj.end_date.strftime('%Y-%m-%d')}")

    def get_grandparent_crumb(self):
        return {"title": "{} {}".format(_("Process"), self.get_object().process.id),
                "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:meeting_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        range = form.cleaned_data["date_range"]
        if range:
            range = range.split("to")
            start_date = datetime.strptime(range[0].strip() + " 12:00", "%Y-%m-%d %H:%M")
            start_date = make_aware(start_date, utc)
            obj.start_date = start_date
            if len(range) > 1:
                end_date = datetime.strptime(range[1].strip() + " 12:00", "%Y-%m-%d %H:%M")
                end_date = make_aware(end_date, utc)
                obj.end_date = end_date
            else:
                obj.end_date = start_date
        else:
            obj.start_date = None
            obj.end_date = None
        obj.updated_by = self.request.user

        old_obj = models.Meeting.objects.get(pk=obj.id)
        obj.save()

        # now for the piece about NCR email
        if obj.process.is_posted and not obj.is_planning and \
                (old_obj.name != obj.name or old_obj.nom != obj.nom or old_obj.location != obj.location or old_obj.tor_display_dates != obj.tor_display_dates):
            if not hasattr(obj.process, "tor"):
                messages.error(self.request, "tried to send an email to NCR but this process has no TOR!")
            else:
                email = emails.UpdatedMeetingEmail(self.request, obj, obj.process.tor, old_obj)
                email.send()
        return HttpResponseRedirect(self.get_success_url())


class MeetingDeleteView(CanModifyProcessRequiredMixin, CommonDeleteView):
    model = models.Meeting
    template_name = 'csas2/confirm_delete.html'
    delete_protection = False
    greatgrandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_grandparent_crumb(self):
        return {"title": "{} {}".format(_("Process"), self.get_object().process.id),
                "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:meeting_detail", args=[self.get_object().id])}

    def get_success_url(self):
        return self.get_grandparent_crumb()["url"]


# meeting files #
#################

class MeetingFileCreateView(CanModifyProcessRequiredMixin, CommonPopoutCreateView):
    model = models.MeetingFile
    form_class = forms.MeetingFileForm
    is_multipart_form_data = True

    def get_initial(self):
        """ For the benefit of the form class"""
        return dict(
            meeting=self.kwargs.get("meeting"),
        )

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.meeting_id = self.kwargs['meeting']
        obj.save()
        if not obj.meeting.somp_notification_date and obj.is_somp:
            email = emails.SoMPEmail(self.request, obj)
            email.send()
            messages.info(self.request, _("A notification email was sent off to the national office!"))
            meeting = obj.meeting
            meeting.somp_notification_date = timezone.now()
            meeting.save()
        return HttpResponseRedirect(self.get_success_url())


class MeetingFileUpdateView(CanModifyProcessRequiredMixin, CommonPopoutUpdateView):
    model = models.MeetingFile
    form_class = forms.MeetingFileForm
    is_multipart_form_data = True

    def form_valid(self, form):
        obj = form.save()
        if not obj.meeting.somp_notification_date and obj.is_somp:
            email = emails.SoMPEmail(self.request, obj)
            email.send()
            messages.info(self.request, _("A notification email was sent off to the national office!"))
            meeting = obj.meeting
            meeting.somp_notification_date = timezone.now()
            meeting.save()
        return HttpResponseRedirect(self.get_success_url())


class MeetingFileDeleteView(CanModifyProcessRequiredMixin, CommonPopoutDeleteView):
    model = models.MeetingFile


# documents #
#############

class DocumentListView(LoginAccessRequiredMixin, CommonFilterView):
    template_name = 'csas2/list.html'
    filterset_class = filters.DocumentFilter
    paginate_by = 25
    home_url_name = "csas2:index"
    row_object_url_name = row_ = "csas2:document_detail"
    container_class = "container-fluid"

    field_list = [
        {"name": 'ttitle|{}'.format("title"), "class": "", "width": "300px"},
        {"name": 'document_type', "class": "", "width": ""},
        {"name": 'process', "class": "", "width": "300px"},
        {"name": 'status', "class": "", "width": ""},
        {"name": 'translation_status', "class": "", "width": ""},
    ]

    def get_queryset(self):
        qp = self.request.GET
        qs = models.Document.objects.filter(document_type__hide_from_list=False)
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
    container_class = ""

    def get_parent_crumb(self):
        return {"title": "{} {}".format(_("Process"), self.get_object().process.id),
                "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = super().get_context_data(**kwargs)
        return context


class DocumentCreateView(CanModifyProcessRequiredMixin, CommonCreateView):
    model = models.Document
    form_class = forms.DocumentForm
    template_name = 'csas2/js_form.html'
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}
    is_multipart_form_data = True

    def get_parent_crumb(self):
        return {"title": "{} {}".format(_("Process"), self.get_process().id), "url": reverse_lazy("csas2:process_detail", args=[self.get_process().id])}

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
    template_name = 'csas2/js_form.html'
    home_url_name = "csas2:index"
    greatgrandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}
    is_multipart_form_data = True

    def get_grandparent_crumb(self):
        return {"title": "{} {}".format(_("Process"), self.get_object().process.id),
                "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

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
    greatgrandparent_crumb = {"title": gettext_lazy("Processes"), "url": reverse_lazy("csas2:process_list")}

    def get_grandparent_crumb(self):
        return {"title": "{} {}".format(_("Process"), self.get_object().process.id),
                "url": reverse_lazy("csas2:process_detail", args=[self.get_object().process.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:document_detail", args=[self.get_object().id])}


# reports #
###########

class ReportSearchFormView(CsasAdminRequiredMixin, CommonFormView):
    template_name = 'csas2/report_search.html'
    form_class = forms.ReportSearchForm
    h1 = gettext_lazy("CSAS Reports")

    def form_valid(self, form):
        report = int(form.cleaned_data["report"])
        fy = form.cleaned_data["fiscal_year"] if form.cleaned_data["fiscal_year"] else "None"

        if report == 1:
            return HttpResponseRedirect(f"{reverse('csas2:meeting_report')}?fiscal_year={fy}")
        messages.error(self.request, "Report is not available. Please select another report.")
        return HttpResponseRedirect(reverse("csas2:reports"))


@login_required()
def meeting_report(request):
    qp = request.GET
    year = None if not qp.get("fiscal_year") else int(qp.get("fiscal_year"))
    file_url = reports.generate_meeting_report(fiscal_year=year)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            fy = get_object_or_404(FiscalYear, pk=year)
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename="CSAS meetings ({fy}).xlsx"'

            return response
    raise Http404
