import math
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.db.models import TextField, Q
from django.db.models.functions import Concat
from django.shortcuts import render
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
###
from easy_pdf.views import PDFTemplateView

from lib.functions.custom_functions import nz, listrify
from . import models
from . import forms
from . import filters
from . import emails
from . import reports
from masterlist import models as ml_models
from shared_models import models as shared_models

ind_organizations = ml_models.Organization.objects.filter(grouping__is_indigenous=True)


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'ihub/close_me.html'


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


class SiteLoginRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class IndexTemplateView(SiteLoginRequiredMixin, TemplateView):
    template_name = 'ihub/index.html'

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, mark_safe(_("Please note that only <b>unclassified information</b> may be entered into this application.")))
        return super().dispatch(request, *args, **kwargs)


# PERSON #
##########

class PersonListView(SiteLoginRequiredMixin, FilterView):
    template_name = 'ihub/person_list.html'
    filterset_class = filters.PersonFilter
    model = ml_models.Person
    queryset = ml_models.Person.objects.annotate(
        search_term=Concat('first_name', 'last_name', 'notes', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = ml_models.Person.objects.first()
        context["field_list"] = [
            'designation',
            'last_name',
            'first_name',
            'phone_1',
            'phone_2',
            'email_1',
            'ihub_vetted',
        ]
        return context


class PersonDetailView(SiteLoginRequiredMixin, DetailView):
    model = ml_models.Person
    template_name = 'ihub/person_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            "designation",
            "first_name",
            "last_name",
            "phone_1",
            "phone_2",
            "email_1",
            "email_2",
            "cell",
            "fax",
            "language",
            "notes",
            "ihub_vetted",
            "last_modified_by",
        ]
        return context


class PersonUpdateView(iHubAdminRequiredMixin, UpdateView):
    model = ml_models.Person
    template_name = 'ihub/person_form.html'
    form_class = forms.PersonForm

    def get_initial(self):
        return {
            'ihub_vetted': True,
            'last_modified_by': self.request.user,
        }

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy('ihub:person_detail', kwargs={"pk": object.id}))


class PersonUpdateViewPopout(iHubAdminRequiredMixin, UpdateView):
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


class PersonCreateView(iHubAdminRequiredMixin, CreateView):
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


class PersonCreateViewPopout(iHubAdminRequiredMixin, CreateView):
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
    success_message = _('The person was deleted successfully!')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# ORGANIZATION #
################

class OrganizationListView(SiteLoginRequiredMixin, FilterView):
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


class OrganizationDetailView(SiteLoginRequiredMixin, DetailView):
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
            'mailing_address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
            'notes',
        ]
        context["field_list_2"] = [
            'legal_band_name',
            'former_name',
            'website',
            'next_election',
            'new_coucil_effective_date',
            'election_term',
            'population_on_reserve',
            'population_off_reserve',
            'population_other_reserve',
            'fin',
            'processing_plant',
            'wharf',
            'consultation_protocol',
            'council_quorum',
            'reserves',
            'orgs',
        ]
        return context


class OrganizationUpdateView(iHubAdminRequiredMixin, UpdateView):
    model = ml_models.Organization
    template_name = 'ihub/organization_form.html'
    form_class = forms.OrganizationForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy('ihub:org_detail', kwargs={'pk': object.id}))


class OrganizationCreateView(iHubAdminRequiredMixin, CreateView):
    model = ml_models.Organization
    template_name = 'ihub/organization_form.html'
    form_class = forms.OrganizationForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy('ihub:org_detail', kwargs={'pk': object.id}))


class OrganizationDeleteView(iHubAdminRequiredMixin, DeleteView):
    model = ml_models.Organization
    template_name = 'ihub/organization_confirm_delete.html'
    success_url = reverse_lazy('ihub:org_list')
    success_message = _('The organization was deleted successfully!')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# MEMBER  (ORGANIZATION PERSON) #
#################################

class MemberCreateView(iHubAdminRequiredMixin, CreateView):
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


class MemberUpdateView(iHubAdminRequiredMixin, UpdateView):
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


class MemberDeleteView(iHubAdminRequiredMixin, DeleteView):
    model = ml_models.OrganizationMember
    template_name = 'ihub/member_confirm_delete_popout.html'
    success_url = reverse_lazy("ihub:close_me")


# ENTRY #
#########

class EntryListView(SiteLoginRequiredMixin, FilterView):
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


class EntryDetailView(SiteLoginRequiredMixin, DetailView):
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


class EntryUpdateView(iHubAdminRequiredMixin, UpdateView):
    model = models.Entry
    form_class = forms.EntryForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class EntryCreateView(iHubAdminRequiredMixin, CreateView):
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
                         _("The entry has been submitted and an email has been sent to the Indigenous Hub Coordinator!"))
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

class NoteCreateView(iHubAdminRequiredMixin, CreateView):
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


class NoteUpdateView(iHubAdminRequiredMixin, UpdateView):
    model = models.EntryNote
    template_name = 'ihub/note_form_popout.html'
    form_class = forms.NoteForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_ihub_admin_group, login_url='/accounts/denied/')
def note_delete(request, pk):
    object = models.EntryNote.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The note has been successfully deleted from the entry."))
    return HttpResponseRedirect(reverse_lazy("ihub:entry_detail", kwargs={"pk": object.entry.id}))


# ENTRYPERSON #
###############

class EntryPersonCreateView(iHubAdminRequiredMixin, CreateView):
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


class EntryPersonUpdateView(iHubAdminRequiredMixin, UpdateView):
    model = models.EntryPerson
    template_name = 'ihub/entry_person_form_popout.html'
    form_class = forms.EntryPersonForm
    login_url = '/accounts/login_required/'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_ihub_admin_group, login_url='/accounts/denied/')
def entry_person_delete(request, pk):
    object = models.EntryPerson.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The person has been successfully deleted from the entry."))
    return HttpResponseRedirect(reverse_lazy("ihub:entry_detail", kwargs={"pk": object.entry.id}))


# FILE #
########

class FileCreateView(iHubAdminRequiredMixin, CreateView):
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


class FileUpdateView(iHubAdminRequiredMixin, UpdateView):
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


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_ihub_admin_group, login_url='/accounts/denied/')
def file_delete(request, pk):
    object = models.File.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The file has been successfully deleted from the entry."))
    return HttpResponseRedirect(reverse_lazy("ihub:entry_detail", kwargs={"pk": object.entry.id}))


# REPORTS #
###########

class ReportSearchFormView(SiteLoginRequiredMixin, FormView):
    template_name = 'ihub/report_search.html'
    form_class = forms.ReportSearchForm

    # def get_initial(self):
    # default the year to the year of the latest samples
    # return {"fiscal_year": fiscal_year()}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        sectors = listrify(form.cleaned_data["sectors"])
        orgs = listrify(form.cleaned_data["organizations"])
        org = int(nz(form.cleaned_data["single_org"]), 0)
        fy = str(form.cleaned_data["fiscal_year"])
        report = int(form.cleaned_data["report"])

        if report == 1:
            return HttpResponseRedirect(reverse("ihub:capacity_xlsx", kwargs=
            {
                "fy": nz(fy, "None"),
                "orgs": nz(orgs, "None"),
                "sectors": nz(sectors, "None"),
            }))

        elif report == 2:
            return HttpResponseRedirect(reverse("ihub:report_q", kwargs={"org": org}))

        elif report == 3:
            return HttpResponseRedirect(reverse("ihub:summary_xlsx", kwargs=
            {
                "fy": nz(fy, "None"),
                "orgs": nz(orgs, "None"),
                "sectors": nz(sectors, "None"),
            }))
        elif report == 4:
            return HttpResponseRedirect(reverse("ihub:summary_pdf", kwargs=
            {
                "fy": nz(fy, "None"),
                "orgs": nz(orgs, "None"),
                "sectors": nz(sectors, "None"),
            }))

        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("ihub:report_search"))


def capacity_export_spreadsheet(request, fy, orgs, sectors):
    file_url = reports.generate_capacity_spreadsheet(fy, orgs, sectors)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="iHub Capacity Report ({}).xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


def summary_export_spreadsheet(request, fy, orgs, sectors):
    file_url = reports.generate_summary_spreadsheet(fy, orgs, sectors)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="iHub Summary Report ({}).xlsx"'.format(timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


class OrganizationCueCard(PDFTemplateView):
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
            'legal_band_name',
            'former_name',
            'website',
        ]
        context["org_field_list_2"] = [
            'address',
            'mailing_address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
        ]
        context["org_field_list_3"] = [
            'next_election',
            'election_term',
            'new_coucil_effective_date',
            'population_on_reserve',
            'population_off_reserve',
            'population_other_reserve',
        ]
        context["org_field_list_4"] = [
            'fin',
            'processing_plant',
            'wharf',
            'consultation_protocol',
            'council_quorum',
            'reserves',
            'orgs',
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


class PDFSummaryReport(PDFTemplateView):
    login_url = '/accounts/login_required/'
    template_name = "ihub/report_pdf_summary.html"

    def get_pdf_filename(self):
        pdf_filename = "iHub Summary Report ({}).pdf".format(timezone.now().strftime("%Y-%m-%d"))
        return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get an entry list for the fiscal year (if any)

        # first, filter out the "none" placeholder
        fy = self.kwargs["fy"]
        sectors = self.kwargs["sectors"]
        orgs = self.kwargs["orgs"]

        if fy == "None":
            fy = None
        if orgs == "None":
            orgs = None
        if sectors == "None":
            sectors = None

        # get an entry list for the fiscal year (if any)
        if fy:
            entry_list = models.Entry.objects.filter(fiscal_year=fy)
            if sectors:
                # we have to refine the queryset to only the selected sectors
                sector_list = [ml_models.Sector.objects.get(pk=int(s)) for s in sectors.split(",")]
                # create the species query object: Q
                q_objects = Q()  # Create an empty Q object to start with
                for s in sector_list:
                    q_objects |= Q(sectors=s)  # 'or' the Q objects together
                # apply the filter
                entry_list = entry_list.filter(q_objects)
            if orgs:
                # we have to refine the queryset to only the selected orgs
                org_list = [ml_models.Organization.objects.get(pk=int(o)) for o in orgs.split(",")]
                # create the species query object: Q
                q_objects = Q()  # Create an empty Q object to start with
                for o in org_list:
                    q_objects |= Q(organizations=o)  # 'or' the Q objects together
                # apply the filter
                entry_list = entry_list.filter(q_objects)

        else:
            entry_list = models.Entry.objects.all()
            if sectors:
                # we have to refine the queryset to only the selected sectors
                sector_list = [ml_models.Sector.objects.get(pk=int(s)) for s in sectors.split(",")]
                # create the species query object: Q
                q_objects = Q()  # Create an empty Q object to start with
                for s in sector_list:
                    q_objects |= Q(sectors=s)  # 'or' the Q objects together
                # apply the filter
                entry_list = entry_list.filter(q_objects)
            if orgs:
                # we have to refine the queryset to only the selected orgs
                org_list = [ml_models.Organization.objects.get(pk=int(o)) for o in orgs.split(",")]
                # create the species query object: Q
                q_objects = Q()  # Create an empty Q object to start with
                for o in org_list:
                    q_objects |= Q(organizations=o)  # 'or' the Q objects together
                # apply the filter
                entry_list = entry_list.filter(q_objects)
        context["entry_list"] = entry_list

        # remove any orgs without entries
        org_list = list(set([org for entry in entry_list for org in entry.organizations.all()]))

        # create a queryset
        if len(org_list) > 0:
            # create the species query object: Q
            q_objects = Q()  # Create an empty Q object to start with
            for o in org_list:
                q_objects |= Q(pk=o.id)  # 'or' the Q objects together
            # apply the filter
            org_list = ml_models.Organization.objects.filter(q_objects).order_by("abbrev")

        context["org_list"] = org_list

        # create a dict for the index page
        my_dict = {}
        for org in org_list:
            my_dict[org.id] = entry_list.filter(organizations=org).order_by("title")
        context["my_dict"] = my_dict

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
@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_ihub_admin_group, login_url='/accounts/denied/')
def manage_sectors(request):
    qs = ml_models.Sector.objects.all()
    if request.method == 'POST':
        formset = forms.SectorFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Sectors have been successfully updated")
            return HttpResponseRedirect(reverse("ihub:manage_sectors"))
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


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_ihub_admin_group, login_url='/accounts/denied/')
def manage_orgs(request):
    qs = ind_organizations
    if request.method == 'POST':
        formset = forms.OrganizationFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Organizations have been successfully updated")
            return HttpResponseRedirect(reverse("ihub:manage_orgs"))
    else:
        formset = forms.OrganizationFormSet(
            queryset=qs)
    context = {}
    context['title'] = "Manage Organizations"
    context['formset'] = formset
    return render(request, 'ihub/manage_settings.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_ihub_admin_group, login_url='/accounts/denied/')
def manage_statuses(request):
    qs = models.Status.objects.all()
    if request.method == 'POST':
        formset = forms.StatusFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Statuses have been successfully updated")
            return HttpResponseRedirect(reverse("ihub:manage_statuses"))
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


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_ihub_admin_group, login_url='/accounts/denied/')
def manage_entry_types(request):
    qs = models.EntryType.objects.all()
    if request.method == 'POST':
        formset = forms.EntryTypeFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Entry types have been successfully updated")
            return HttpResponseRedirect(reverse("ihub:manage_entry_types"))
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


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_ihub_admin_group, login_url='/accounts/denied/')
def manage_funding_purposes(request):
    qs = models.FundingPurpose.objects.all()
    if request.method == 'POST':
        formset = forms.FundingPurposeFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Funding purposes have been successfully updated")
            return HttpResponseRedirect(reverse("ihub:manage_funding_purposes"))
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



@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_ihub_admin_group, login_url='/accounts/denied/')
def manage_reserves(request):
    qs = ml_models.Reserve.objects.all()
    if request.method == 'POST':
        formset = forms.ReserveFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Reverse list has been successfully updated")
            return HttpResponseRedirect(reverse("ihub:manage_reserves"))
    else:
        formset = forms.ReserveFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
    ]
    context['title'] = "Manage Reserve List"
    context['formset'] = formset
    return render(request, 'ihub/manage_settings_small.html', context)
