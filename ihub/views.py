import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.db.models import TextField
from django.db.models.functions import Concat
from django.utils import timezone
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import  UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
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


class IndexTemplateView(iHubAccessRequiredMixin, TemplateView):
    template_name = 'ihub/index.html'


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
            'abbrev',
            'address',
            'city',
            'postal_code',
            'province.abbrev_eng',
            # 'grouping',
        ]
        return context

class OrganizationUpdateView(iHubAccessRequiredMixin, UpdateView):
    model = models.Organization
    form_class = forms.OrganizationForm
    success_url = reverse_lazy('ihub:org_list')


class OrganizationCreateView(iHubAccessRequiredMixin, CreateView):
    model = models.Organization
    form_class = forms.OrganizationForm
    success_url = reverse_lazy('ihub:org_list')


class OrganizationDeleteView(iHubAccessRequiredMixin, DeleteView):
    model = models.Organization
    success_url = reverse_lazy('ihub:org_list')
    success_message = 'The organization was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)



# ENTRY #
#########

class EntryListView(iHubAccessRequiredMixin, FilterView):
    template_name = "ihub/entry_list.html"
    model = models.Entry
    filterset_class = filters.EntryFilter


class EntryDetailView(iHubAccessRequiredMixin, DetailView):
    model = models.Entry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'title',
            'organization',
            'status',
            'sector',
            'entry_type',
            'initial_date',
            'region',
            'funding_needed',
            'funding_requested',
            'amount_expected',
            'transferred',
            'amount_transferred',
            'fiscal_year',
            'funding_purpose',
            'date_last_modified',
            'date_created',
            'last_modified_by',
            'created_by',
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
        self.object = form.save()

        # create a new email object
        email = emails.NewEntryEmail(self.object)
        # send the email object
        if settings.MY_ENVR != 'dev':
            send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
                      recipient_list=email.to_list, fail_silently=False, )
        else:
            print('not sending email since in dev mode')
        messages.success(self.request,
                         "The entry has been submitted and an email has been sent to the Indigenous Hub Coordinator!")
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'created_by': self.request.user
        }


class EntryDeleteView(iHubAccessRequiredMixin, DeleteView):
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
        if object.user:
            object.organization = "DFO"
        object.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


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
                return HttpResponseRedirect(reverse("ihub:capacity_xlsx", kwargs={"fy": fy,}))
            elif orgs:
                return HttpResponseRedirect(reverse("ihub:capacity_xlsx", kwargs={"orgs": orgs,}))
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


#
# def report_species_count(request, species_list):
#     reports.generate_species_count_report(species_list)
#     # find the name of the file
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     target_dir = os.path.join(base_dir, 'templates', 'camp', 'temp')
#     for root, dirs, files in os.walk(target_dir):
#         for file in files:
#             if "report_temp" in file:
#                 my_file = "camp/temp/{}".format(file)
#
#     return render(request, "camp/report_display.html", {"report_path": my_file})
#
#
# def report_species_richness(request, site=None):
#     if site:
#         reports.generate_species_richness_report(site)
#     else:
#         reports.generate_species_richness_report()
#
#     return render(request, "camp/report_display.html")
#
#
# class AnnualWatershedReportTemplateView(PDFTemplateView):
#     template_name = 'camp/report_watershed_display.html'
#
#     def get_pdf_filename(self):
#         site = models.Site.objects.get(pk=self.kwargs['site']).site
#         return "{} Annual Report {}.pdf".format(self.kwargs['year'], site)
#
#     def get_context_data(self, **kwargs):
#         reports.generate_annual_watershed_report(self.kwargs["site"], self.kwargs["year"])
#         site = models.Site.objects.get(pk=self.kwargs['site']).site
#         return super().get_context_data(
#             pagesize="A4 landscape",
#             title="Annual Report for {}_{}".format(site, self.kwargs['year']),
#             **kwargs
#         )
#
#

#
#
# def fgp_export(request):
#
#     response = reports.generate_fgp_export()
#     return response
#
