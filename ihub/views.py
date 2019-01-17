from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.db.models import Value, TextField, Q
from django.db.models.functions import Concat
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import Context, loader
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
###
from easy_pdf.views import PDFTemplateView

from accounts import models as accounts_models
from collections import OrderedDict

from lib.functions.nz import nz
from . import models
from . import forms
from . import filters
from . import emails


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'ihub/close_me.html'


class IndexTemplateView(TemplateView):
    template_name = 'ihub/index.html'


# ENTRY #
#########

class EntryListView(LoginRequiredMixin, FilterView):
    login_url = '/accounts/login_required/'
    template_name = "ihub/entry_list.html"
    model = models.Entry
    filterset_class = filters.EntryFilter


class EntryDetailView(LoginRequiredMixin, DetailView):
    model = models.Entry
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'title',
            'sector',
            'entry_type',
            'subject',
            'initial_date',
            'leads',
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


class EntryUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Entry
    login_url = '/accounts/login_required/'
    form_class = forms.EntryForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class EntryCreateView(LoginRequiredMixin, CreateView):
    model = models.Entry
    login_url = '/accounts/login_required/'
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
        messages.success(self.request, "The entry has been submitted and an email has been sent to the Indigenous Hub Coordinator!")
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'created_by': self.request.user
        }


class EntryDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Entry
    permission_required = "__all__"
    success_url = reverse_lazy('ihub:entry_list')
    success_message = _('The entry was successfully deleted!')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# NOTES #
#########

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = models.EntryNote
    template_name = 'ihub/note_form_popout.html'
    login_url = '/accounts/login_required/'
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


class NoteUpdateView(LoginRequiredMixin, UpdateView):
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
    return HttpResponseRedirect(reverse_lazy("ihub:entry_detail", kwargs={"pk": object.project.id}))


# # COLLABORATOR #
# ################
#
# class CollaboratorCreateView(LoginRequiredMixin, CreateView):
#     model = models.Collaborator
#     template_name = 'projects/collaborator_form_popout.html'
#     login_url = '/accounts/login_required/'
#     form_class = forms.CollaboratorForm
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         return {
#             'project': project,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = models.Project.objects.get(id=self.kwargs['project'])
#         context['project'] = project
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects:close_me'))
#
#
# class CollaboratorUpdateView(LoginRequiredMixin, UpdateView):
#     model = models.Collaborator
#     template_name = 'projects/collaborator_form_popout.html'
#     form_class = forms.CollaboratorForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects:close_me'))
#
#
# def collaborator_delete(request, pk):
#     object = models.Collaborator.objects.get(pk=pk)
#     object.delete()
#     messages.success(request, _("The collaborator has been successfully deleted from project."))
#     return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))
#
#
# # AGREEMENTS #
# ##############
#
# class AgreementCreateView(LoginRequiredMixin, CreateView):
#     model = models.CollaborativeAgreement
#     template_name = 'projects/agreement_form_popout.html'
#     login_url = '/accounts/login_required/'
#     form_class = forms.AgreementForm
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         return {
#             'project': project,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = models.Project.objects.get(id=self.kwargs['project'])
#         context['project'] = project
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects:close_me'))
#
#
# class AgreementUpdateView(LoginRequiredMixin, UpdateView):
#     model = models.CollaborativeAgreement
#     template_name = 'projects/agreement_form_popout.html'
#     form_class = forms.AgreementForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects:close_me'))
#
#
# def agreement_delete(request, pk):
#     object = models.CollaborativeAgreement.objects.get(pk=pk)
#     object.delete()
#     messages.success(request, _("The agreement has been successfully deleted."))
#     return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))
#
#
# # OM COSTS #
# ############
#
# class OMCostCreateView(LoginRequiredMixin, CreateView):
#     model = models.OMCost
#     template_name = 'projects/cost_form_popout.html'
#     login_url = '/accounts/login_required/'
#     form_class = forms.OMCostForm
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         return {
#             'project': project,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = models.Project.objects.get(id=self.kwargs['project'])
#         context['project'] = project
#         context['cost_type'] = "O&M"
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects:close_me'))
#
#
# class OMCostUpdateView(LoginRequiredMixin, UpdateView):
#     model = models.OMCost
#     template_name = 'projects/cost_form_popout.html'
#     form_class = forms.OMCostForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects:close_me'))
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['cost_type'] = _("O&M")
#         return context
#
#
# def om_cost_delete(request, pk):
#     object = models.OMCost.objects.get(pk=pk)
#     object.delete()
#     messages.success(request, _("The cost has been successfully deleted."))
#     return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))
#
#
# # CAPITAL COSTS #
# #################
#
# class CapitalCostCreateView(LoginRequiredMixin, CreateView):
#     model = models.CapitalCost
#     template_name = 'projects/cost_form_popout.html'
#     login_url = '/accounts/login_required/'
#     form_class = forms.CapitalCostForm
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         return {
#             'project': project,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = models.Project.objects.get(id=self.kwargs['project'])
#         context['project'] = project
#         context['cost_type'] = "Capital"
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects:close_me'))
#
#
# class CapitalCostUpdateView(LoginRequiredMixin, UpdateView):
#     model = models.CapitalCost
#     template_name = 'projects/cost_form_popout.html'
#     form_class = forms.CapitalCostForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['cost_type'] = "Capital"
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects:close_me'))
#
#
# def capital_cost_delete(request, pk):
#     object = models.CapitalCost.objects.get(pk=pk)
#     object.delete()
#     messages.success(request, _("The cost has been successfully deleted."))
#     return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))
#
#
# # GC COSTS #
# ############
#
# class GCCostCreateView(LoginRequiredMixin, CreateView):
#     model = models.GCCost
#     template_name = 'projects/cost_form_popout.html'
#     login_url = '/accounts/login_required/'
#     form_class = forms.GCCostForm
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         return {
#             'project': project,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = models.Project.objects.get(id=self.kwargs['project'])
#         context['project'] = project
#         context['cost_type'] = "G&C"
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects:close_me'))
#
#
# class GCCostUpdateView(LoginRequiredMixin, UpdateView):
#     model = models.GCCost
#     template_name = 'projects/cost_form_popout.html'
#     form_class = forms.GCCostForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects:close_me'))
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['cost_type'] = "G&C"
#         return context
#
#
# def gc_cost_delete(request, pk):
#     object = models.GCCost.objects.get(pk=pk)
#     object.delete()
#     messages.success(request, _("The cost has been successfully deleted."))
#     return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))
