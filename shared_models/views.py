from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView
###
from . import models
from . import forms


class CloserTemplateView(TemplateView):
    template_name = 'shared_models/close_me.html'


class CloserNoRefreshTemplateView(TemplateView):
    template_name = 'shared_models/close_me_no_refresh.html'


# SECTION #
###########

class SectionUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Section
    template_name = 'shared_models/section_form.html'
    form_class = forms.SectionForm

    def get_initial(self):
        return {
            "last_modified_by": self.request.user,
        }

    def form_valid(self, form):
        object = form.save()

        # finally close the form
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SectionCreateView(LoginRequiredMixin, CreateView):
    model = models.Section
    template_name = 'shared_models/section_form.html'
    form_class = forms.SectionForm

    def get_initial(self):
        return {
            "last_modified_by": self.request.user,
        }

    def form_valid(self, form):
        object = form.save()

        # finally close the form
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SectionDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Section
    success_url = reverse_lazy('shared_models:close_me')
    success_message = 'The section was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class DivisionCreateView(LoginRequiredMixin, CreateView):
    model = models.Division
    template_name = 'shared_models/division_form.html'
    form_class = forms.DivisionForm

    def form_valid(self, form):
        object = form.save()
        # finally close the form
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_initial(self):
        return {
            "last_modified_by": self.request.user,
        }


class BranchCreateView(LoginRequiredMixin, CreateView):
    model = models.Branch
    template_name = 'shared_models/branch_form.html'
    form_class = forms.BranchForm

    def form_valid(self, form):
        object = form.save()
        # finally close the form
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_initial(self):
        return {
            "last_modified_by": self.request.user,
        }
