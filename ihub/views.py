import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.db.models import TextField
from django.db.models.functions import Concat
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
###
from . import models
from . import forms
from . import filters
from . import emails
from . import reports


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'ihub/close_me.html'


def not_in_ihub_group(user):
    if user:
        return user.groups.filter(name='ihub_access').count() != 0


class iHubAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return not_in_ihub_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


def not_in_ihub_admin_group(user):
    if user:
        return user.groups.filter(name='ihub_admin').count() != 0


class iHubAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return not_in_ihub_admin_group(self.request.user)

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
    model = models.Person
    queryset = models.Person.objects.annotate(
        search_term=Concat('first_name', 'last_name', 'notes', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Person.objects.first()
        context["field_list"] = [
            'last_name',
            'first_name',
            'phone_1',
            'phone_2',
            'email',
        ]
        return context


class PersonDetailView(iHubAccessRequiredMixin, DetailView):
    model = models.Person

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'first_name',
            'last_name',
            'phone_1',
            'phone_2',
            'fax',
            'email',
            'notes',
        ]
        return context


class PersonUpdateView(iHubAccessRequiredMixin, UpdateView):
    model = models.Person
    form_class = forms.PersonForm


class PersonUpdateViewPopout(iHubAccessRequiredMixin, UpdateView):
    template_name = 'ihub/person_form_popout.html'
    model = models.Person
    form_class = forms.PersonForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


class PersonCreateView(iHubAccessRequiredMixin, CreateView):
    model = models.Organization
    form_class = forms.PersonForm


class PersonCreateViewPopout(iHubAccessRequiredMixin, CreateView):
    template_name = 'ihub/person_form_popout.html'
    model = models.Person
    form_class = forms.PersonForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


class PersonDeleteView(iHubAdminRequiredMixin, DeleteView):
    model = models.Person
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
    model = models.Organization
    queryset = models.Organization.objects.annotate(
        search_term=Concat('name_eng', 'name_fre', 'abbrev', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Organization.objects.first()
        context["field_list"] = [
            'name_eng',
            'name_fre',
            'name_ind',
            'province',
        ]
        return context


class OrganizationDetailView(iHubAccessRequiredMixin, DetailView):
    model = models.Organization

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
    model = models.Organization
    form_class = forms.OrganizationForm


class OrganizationCreateView(iHubAccessRequiredMixin, CreateView):
    model = models.Organization
    form_class = forms.OrganizationForm


class OrganizationDeleteView(iHubAdminRequiredMixin, DeleteView):
    model = models.Organization
    success_url = reverse_lazy('ihub:org_list')
    success_message = 'The organization was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# MEMBER  (ORGANIZATION PERSON) #
#################################

class MemberCreateView(iHubAccessRequiredMixin, CreateView):
    model = models.OrganizationMember
    template_name = 'ihub/member_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.MemberForm

    def get_initial(self):
        org = models.Organization.objects.get(pk=self.kwargs['org'])
        return {
            'organization': org,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = models.Organization.objects.get(id=self.kwargs['org'])
        context['organization'] = org

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in models.Person.objects.all()
        ]

        context['person_list'] = person_list

        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


class MemberUpdateView(iHubAccessRequiredMixin, UpdateView):
    model = models.OrganizationMember
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
            ) for p in models.Person.objects.all()
        ]

        context['person_list'] = person_list

        return context


def member_delete(request, pk):
    object = models.OrganizationMember.objects.get(pk=pk)
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
            'fiscal_year',
            'last_modified_by',
            'created_by',
        ]

        context["field_list_1"] = [
            'funding_needed',
            'funding_purpose',
            'amount_requested',
            'amount_approved',
            'amount_transferred',
            'amount_lapsed',
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
        if settings.MY_ENVR != 'dev':
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
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("ihub:report_search"))


def capacity_export_spreadsheet(request, fy=None, orgs=None):
    file_url = reports.generate_capacity_spreadsheet(fy, orgs)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="iHub export {}.xlsx"'.format(timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


# SETTINGS #
############

def manage_sectors(request):
    qs = models.Sector.objects.all()
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


def manage_roles(request):
    qs = models.MemberRole.objects.all()
    if request.method == 'POST':
        formset = forms.MemberRoleFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Member roles have been successfully updated")
    else:
        formset = forms.MemberRoleFormSet(
            queryset=qs)
    context = {}
    context['title'] = "Manage Member Roles"
    context['formset'] = formset
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
    ]
    return render(request, 'ihub/manage_settings_small.html', context)


def manage_orgs(request):
    qs = models.Organization.objects.all()
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
