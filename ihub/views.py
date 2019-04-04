import math
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.db.models import TextField, Q
from django.db.models.functions import Concat
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
###
from easy_pdf.views import PDFTemplateView

from lib.functions.nz import nz
from . import models
from . import forms
from . import filters
from . import emails
from . import reports
from masterlist import models as ml_models

ind_organizations = ml_models.Organization.objects.filter(grouping__is_indigenous=True)


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'ihub/close_me.html'


def in_ihub_group(user):
    if user:
        return user.groups.filter(name='ihub_access').count() != 0


class iHubAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_ihub_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


def in_ihub_admin_group(user):
    if user:
        return user.groups.filter(name='ihub_admin').count() != 0


class iHubAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_ihub_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class IndexTemplateView(iHubAccessRequiredMixin, TemplateView):
    template_name = 'ihub/index.html'


# PERSON #
##########

class PersonListView(iHubAccessRequiredMixin, FilterView):
    template_name = 'ihub/person_list.html'
    filterset_class = filters.PersonFilter
    model = ml_models.Person
    queryset = ml_models.Person.objects.annotate(
        search_term=Concat('first_name', 'last_name', 'notes', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = ml_models.Person.objects.first()
        context["field_list"] = [
            'last_name',
            'first_name',
            'phone_1',
            'phone_2',
            'email_1',
        ]
        return context


class PersonDetailView(iHubAccessRequiredMixin, DetailView):
    model = ml_models.Person
    template_name = 'ihub/person_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'first_name',
            'last_name',
            'phone_1',
            'phone_2',
            'fax',
            'email_1',
            'email_2',
            'notes',
            'last_modified_by',
        ]
        return context


class PersonUpdateView(iHubAccessRequiredMixin, UpdateView):
    model = ml_models.Person
    template_name = 'ihub/person_form.html'
    form_class = forms.PersonForm

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy('ihub:person_detail', kwargs={"pk": object.id}))


class PersonUpdateViewPopout(iHubAccessRequiredMixin, UpdateView):
    template_name = 'ihub/person_form_popout.html'
    model = ml_models.Person
    form_class = forms.PersonForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }


class PersonCreateView(iHubAccessRequiredMixin, CreateView):
    model = ml_models.Organization
    template_name = 'ihub/person_form.html'
    form_class = forms.PersonForm

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy('ihub:person_detail', kwargs={"pk": object.id}))


class PersonCreateViewPopout(iHubAccessRequiredMixin, CreateView):
    model = ml_models.Person
    template_name = 'ihub/person_form_popout.html'
    form_class = forms.PersonForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }


class PersonDeleteView(iHubAdminRequiredMixin, DeleteView):
    model = ml_models.Person
    template_name = 'ihub/person_confirm_delete.html'
    success_url = reverse_lazy('ihub:person_list')
    success_message = 'The person was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# ORGANIZATION #
################

class OrganizationListView(iHubAccessRequiredMixin, FilterView):
    template_name = 'ihub/organization_list.html'
    filterset_class = filters.OrganizationFilter
    queryset = ind_organizations.annotate(
        search_term=Concat('name_eng', 'name_fre', 'abbrev', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = ml_models.Organization.objects.first()
        context["field_list"] = [
            'name_eng',
            'name_fre',
            'name_ind',
            'province',
            'grouping',
            'full_address|' + _("Full address"),
        ]
        return context


class OrganizationDetailView(iHubAccessRequiredMixin, DetailView):
    model = ml_models.Organization
    template_name = 'ihub/organization_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name_eng',
            'name_fre',
            'name_ind',
            'abbrev',
            'address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
        ]
        context["field_list_2"] = [
            'next_election',
            'election_term',
            'population_on_reserve',
            'population_off_reserve',
            'population_other_reserve',
            'fin',
            'notes',
        ]
        return context


class OrganizationUpdateView(iHubAccessRequiredMixin, UpdateView):
    model = ml_models.Organization
    template_name = 'ihub/organization_form.html'
    form_class = forms.OrganizationForm


class OrganizationCreateView(iHubAccessRequiredMixin, CreateView):
    model = ml_models.Organization
    template_name = 'ihub/organization_form.html'
    form_class = forms.OrganizationForm


class OrganizationDeleteView(iHubAdminRequiredMixin, DeleteView):
    model = ml_models.Organization
    template_name = 'ihub/organization_confirm_delete.html'
    success_url = reverse_lazy('ihub:org_list')
    success_message = 'The organization was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# MEMBER  (ORGANIZATION PERSON) #
#################################

class MemberCreateView(iHubAccessRequiredMixin, CreateView):
    model = ml_models.OrganizationMember
    template_name = 'ihub/member_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.MemberForm

    def get_initial(self):
        org = ml_models.Organization.objects.get(pk=self.kwargs['org'])
        return {
            'organization': org,
            'last_modified_by': self.request.user,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = ml_models.Organization.objects.get(id=self.kwargs['org'])
        context['organization'] = org

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in ml_models.Person.objects.all()
        ]

        context['person_list'] = person_list

        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


class MemberUpdateView(iHubAccessRequiredMixin, UpdateView):
    model = ml_models.OrganizationMember
    template_name = 'ihub/member_form_popout.html'
    form_class = forms.MemberForm
    login_url = '/accounts/login_required/'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in ml_models.Person.objects.all()
        ]

        context['person_list'] = person_list

        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }


def member_delete(request, pk):
    object = ml_models.OrganizationMember.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The member has been successfully deleted from the organization."))
    return HttpResponseRedirect(reverse_lazy("ihub:org_detail", kwargs={"pk": object.organization.id}))


# ENTRY #
#########

class EntryListView(iHubAccessRequiredMixin, FilterView):
    template_name = "ihub/entry_list.html"
    model = models.Entry
    filterset_class = filters.EntryFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Entry.objects.first()
        context["field_list"] = [
            'title',
            'entry_type',
            'regions',
            'organizations',
            'sectors',
            'status',
        ]
        return context


class EntryDetailView(iHubAccessRequiredMixin, DetailView):
    model = models.Entry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'title',
            'organizations',
            'status',
            'sectors',
            'entry_type',
            'initial_date',
            'regions',
            'last_modified_by',
            'created_by',
        ]

        context["field_list_1"] = [
            'fiscal_year',
            'funding_needed',
            'funding_purpose',
            'amount_requested',
            'amount_approved',
            'amount_transferred',
            'amount_lapsed',
            'amount_owing'
        ]

        return context


class EntryUpdateView(iHubAccessRequiredMixin, UpdateView):
    model = models.Entry
    form_class = forms.EntryForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class EntryCreateView(iHubAccessRequiredMixin, CreateView):
    model = models.Entry
    form_class = forms.EntryCreateForm

    def form_valid(self, form):
        object = form.save()

        models.EntryPerson.objects.create(entry=object, role=1, user_id=self.request.user.id, organization="DFO")

        # create a new email object
        email = emails.NewEntryEmail(object)
        # send the email object
        if settings.PRODUCTION_SERVER:
            send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
                      recipient_list=email.to_list, fail_silently=False, )
        else:
            print('not sending email since in dev mode')
        messages.success(self.request,
                         "The entry has been submitted and an email has been sent to the Indigenous Hub Coordinator!")
        return HttpResponseRedirect(reverse_lazy('ihub:entry_detail', kwargs={"pk": object.id}))

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'created_by': self.request.user
        }


class EntryDeleteView(iHubAdminRequiredMixin, DeleteView):
    model = models.Entry
    success_url = reverse_lazy('ihub:entry_list')
    success_message = _('The entry was successfully deleted!')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# NOTES #
#########

class NoteCreateView(iHubAccessRequiredMixin, CreateView):
    model = models.EntryNote
    template_name = 'ihub/note_form_popout.html'
    form_class = forms.NoteForm

    def get_initial(self):
        entry = models.Entry.objects.get(pk=self.kwargs['entry'])
        return {
            'author': self.request.user,
            'entry': entry,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = models.Entry.objects.get(id=self.kwargs['entry'])
        context['entry'] = entry
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


class NoteUpdateView(iHubAccessRequiredMixin, UpdateView):
    model = models.EntryNote
    template_name = 'ihub/note_form_popout.html'
    form_class = forms.NoteForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


def note_delete(request, pk):
    object = models.EntryNote.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The note has been successfully deleted from the entry."))
    return HttpResponseRedirect(reverse_lazy("ihub:entry_detail", kwargs={"pk": object.entry.id}))


# ENTRYPERSON #
###############

class EntryPersonCreateView(iHubAccessRequiredMixin, CreateView):
    model = models.EntryPerson
    template_name = 'ihub/entry_person_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.EntryPersonForm

    def get_initial(self):
        entry = models.Entry.objects.get(pk=self.kwargs['entry'])
        return {
            'entry': entry,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = models.Entry.objects.get(id=self.kwargs['entry'])
        context['entry'] = entry
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


class EntryPersonUpdateView(iHubAccessRequiredMixin, UpdateView):
    model = models.EntryPerson
    template_name = 'ihub/entry_person_form_popout.html'
    form_class = forms.EntryPersonForm
    login_url = '/accounts/login_required/'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


def entry_person_delete(request, pk):
    object = models.EntryPerson.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The person has been successfully deleted from the entry."))
    return HttpResponseRedirect(reverse_lazy("ihub:entry_detail", kwargs={"pk": object.entry.id}))


# FILE #
########

class FileCreateView(iHubAccessRequiredMixin, CreateView):
    model = models.File
    template_name = 'ihub/file_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.FileForm
    success_url = reverse_lazy('ihub:close_me')

    def get_initial(self):
        entry = models.Entry.objects.get(pk=self.kwargs['entry'])
        return {
            'entry': entry,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = models.Entry.objects.get(id=self.kwargs['entry'])
        context['entry'] = entry
        return context


class FileUpdateView(iHubAccessRequiredMixin, UpdateView):
    model = models.File
    template_name = 'ihub/file_form_popout.html'
    form_class = forms.FileForm
    login_url = '/accounts/login_required/'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))

    def get_initial(self):
        entry = models.Entry.objects.get(pk=self.kwargs['entry'])
        return {
            'date_uploaded': timezone.now(),
        }


def file_delete(request, pk):
    object = models.File.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The file has been successfully deleted from the entry."))
    return HttpResponseRedirect(reverse_lazy("ihub:entry_detail", kwargs={"pk": object.entry.id}))


# REPORTS #
###########

class ReportSearchFormView(iHubAccessRequiredMixin, FormView):
    template_name = 'ihub/report_search.html'
    form_class = forms.ReportSearchForm

    # def get_initial(self):
    # default the year to the year of the latest samples
    # return {"fiscal_year": fiscal_year()}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        orgs = str(form.cleaned_data["organizations"]).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")
        org = int(nz(form.cleaned_data["single_org"]), 0)
        fy = str(form.cleaned_data["fiscal_year"])
        report = int(form.cleaned_data["report"])

        if report == 1:
            if fy and orgs:
                return HttpResponseRedirect(reverse("ihub:capacity_xlsx", kwargs={"fy": fy, "orgs": orgs}))
            elif fy:
                return HttpResponseRedirect(reverse("ihub:capacity_xlsx", kwargs={"fy": fy, }))
            elif orgs:
                return HttpResponseRedirect(reverse("ihub:capacity_xlsx", kwargs={"orgs": orgs, }))
            else:
                return HttpResponseRedirect(reverse("ihub:capacity_xlsx"))
        elif report == 2:
            return HttpResponseRedirect(reverse("ihub:report_q", kwargs={"org": org}))
        elif report == 3:
            if fy and orgs:
                return HttpResponseRedirect(reverse("ihub:summary_xlsx", kwargs={"fy": fy, "orgs": orgs}))
            elif fy:
                return HttpResponseRedirect(reverse("ihub:summary_xlsx", kwargs={"fy": fy, "orgs": "None"}))
            elif orgs:
                return HttpResponseRedirect(reverse("ihub:summary_xlsx", kwargs={"fy": "None", "orgs": orgs}))
            else:
                return HttpResponseRedirect(reverse("ihub:summary_xlsx", kwargs={"fy": "None", "orgs": "None"}))
        elif report == 4:
            if fy and orgs:
                return HttpResponseRedirect(reverse("ihub:summary_pdf", kwargs={"fy": fy, "orgs": orgs}))
            elif fy:
                return HttpResponseRedirect(reverse("ihub:summary_pdf", kwargs={"fy": fy, "orgs": "None"}))
            elif orgs:
                return HttpResponseRedirect(reverse("ihub:summary_pdf", kwargs={"fy": "None", "orgs": orgs}))
            else:
                return HttpResponseRedirect(reverse("ihub:summary_pdf", kwargs={"fy": "None", "orgs": "None"}))
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("ihub:report_search"))


def capacity_export_spreadsheet(request, fy=None, orgs=None):
    file_url = reports.generate_capacity_spreadsheet(fy, orgs)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="iHub Capacity Report ({}).xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


def summary_export_spreadsheet(request, fy, orgs):
    file_url = reports.generate_summary_spreadsheet(fy, orgs)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="iHub Summary Report ({}).xlsx"'.format(timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


class OrganizationCueCard(iHubAccessRequiredMixin, PDFTemplateView):
    template_name = "ihub/report_cue_card.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = ml_models.Organization.objects.get(pk=self.kwargs["org"])
        context["org"] = org
        context["org_field_list_1"] = [
            'name_eng',
            'name_fre',
            'name_ind',
            'abbrev',
        ]
        context["org_field_list_2"] = [
            'address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
        ]
        context["org_field_list_3"] = [
            'next_election',
            'election_term',
            'population_on_reserve',
            'population_off_reserve',
            'population_other_reserve',
        ]
        context["org_field_list_4"] = [
            'fin',
            'notes',
        ]

        # determine how many rows for the table
        context["contact_table_rows"] = range(0, math.ceil(org.members.count() / 4))
        context["one_to_four"] = range(0, 4)

        context["entry_field_list_1"] = [
            'fiscal_year',
            'initial_date',
            'status',
        ]
        context["entry_field_list_2"] = [
            'sectors',
            'entry_type',
            'regions',
        ]
        context["entry_field_list_3"] = [
            'funding_needed',
            'funding_purpose',
            'amount_requested',
        ]
        context["entry_field_list_4"] = [
            'amount_approved',
            'amount_transferred',
            'amount_lapsed',
        ]
        context["entry_field_list_5"] = [
            'amount_owing',
        ]
        context["now"] = timezone.now()
        return context


class PDFSummaryReport(LoginRequiredMixin, PDFTemplateView):
    login_url = '/accounts/login_required/'
    template_name = "ihub/report_pdf_summary.html"

    def get_pdf_filename(self):
        pdf_filename = "iHub Summary Report ({}).pdf".format(timezone.now().strftime("%Y-%m-%d"))
        return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get an entry list for the fiscal year (if any)
        if self.kwargs["orgs"] != "None":
            org_list = [ml_models.Organization.objects.get(pk=int(o)) for o in self.kwargs["orgs"].split(",")]
        else:
            org_list = ml_models.Organization.objects.filter(grouping__is_indigenous=True)

        # remove any orgs without entries
        org_list = [org for org in org_list if org.entries.count() > 0]
        context["org_list"] = org_list

        my_dict = {}
        for org in org_list:
            if org.entries.count() > 0:
                if self.kwargs["fy"] != "None":
                    entry_list = org.entries.filter(fiscal_year=self.kwargs["fy"])
                else:
                    entry_list = org.entries.all()
                my_dict[org.id] = entry_list.order_by("title")

        context["my_dict"] = my_dict

        q_objects = Q()  # Create an empty Q object to start with
        for org in org_list:
            q_objects |= Q(organizations=org)  # 'or' the Q objects together
        entry_list = models.Entry.objects.filter(q_objects).order_by("title")

        context["entry_list"] = entry_list

        context["fy"] = self.kwargs["fy"]
        context["field_list"] = [
            'title',
            'organizations',
            'status',
            'sectors',
            'entry_type',
            'initial_date',
            'regions',
            'created_by',
        ]

        context["field_list_1"] = [
            'fiscal_year',
            'funding_needed',
            'funding_purpose',
            'amount_requested',
            'amount_approved',
            'amount_transferred',
            'amount_lapsed',
            'amount_owing'
        ]


        return context


# SETTINGS #
############

def manage_sectors(request):
    qs = ml_models.Sector.objects.all()
    if request.method == 'POST':
        formset = forms.SectorFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Sectors have been successfully updated")
    else:
        formset = forms.SectorFormSet(
            queryset=qs)
    context = {}
    context['title'] = "Manage Sectors"
    context['formset'] = formset
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
    ]
    return render(request, 'ihub/manage_settings_small.html', context)


#
# def manage_roles(request):
#     qs = models.MemberRole.objects.all()
#     if request.method == 'POST':
#         formset = forms.MemberRoleFormSet(request.POST, )
#         if formset.is_valid():
#             formset.save()
#             # do something with the formset.cleaned_data
#             messages.success(request, "Member roles have been successfully updated")
#     else:
#         formset = forms.MemberRoleFormSet(
#             queryset=qs)
#     context = {}
#     context['title'] = "Manage Member Roles"
#     context['formset'] = formset
#     context["my_object"] = qs.first()
#     context["field_list"] = [
#         'name',
#         'nom',
#     ]
#     return render(request, 'ihub/manage_settings_small.html', context)


def manage_orgs(request):
    qs = ind_organizations
    if request.method == 'POST':
        formset = forms.OrganizationFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Organizations have been successfully updated")
    else:
        formset = forms.OrganizationFormSet(
            queryset=qs)
    context = {}
    context['title'] = "Manage Organizations"
    context['formset'] = formset
    return render(request, 'ihub/manage_settings.html', context)


def manage_statuses(request):
    qs = models.Status.objects.all()
    if request.method == 'POST':
        formset = forms.StatusFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Statuses have been successfully updated")
    else:
        formset = forms.StatusFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
        'color',
    ]
    context['title'] = "Manage Statuses"
    context['formset'] = formset
    return render(request, 'ihub/manage_settings_small.html', context)


def manage_entry_types(request):
    qs = models.EntryType.objects.all()
    if request.method == 'POST':
        formset = forms.EntryTypeFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Entry types have been successfully updated")
    else:
        formset = forms.EntryTypeFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
        'color',
    ]
    context['title'] = "Manage Entry Types"
    context['formset'] = formset
    return render(request, 'ihub/manage_settings_small.html', context)


def manage_funding_purposes(request):
    qs = models.FundingPurpose.objects.all()
    if request.method == 'POST':
        formset = forms.FundingPurposeFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Funding purposes have been successfully updated")
    else:
        formset = forms.FundingPurposeFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
    ]
    context['title'] = "Manage Funding Purposes"
    context['formset'] = formset
    return render(request, 'ihub/manage_settings_small.html', context)


def manage_regions(request):
    qs = ml_models.Region.objects.all()
    if request.method == 'POST':
        formset = forms.RegionFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "DFO regions have been successfully updated")
    else:
        formset = forms.RegionFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
    ]
    context['title'] = "Manage DFO Regions"
    context['formset'] = formset
    return render(request, 'ihub/manage_settings_small.html', context)


def manage_groupings(request):
    qs = ml_models.Grouping.objects.filter(is_indigenous=True)
    if request.method == 'POST':
        formset = forms.GroupingFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Groupings have been successfully updated")
    else:
        formset = forms.GroupingFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
    ]
    context['title'] = "Manage Groupings"
    context['formset'] = formset
    return render(request, 'ihub/manage_settings_small.html', context)
