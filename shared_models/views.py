from abc import ABC

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


# CommonCreate Extends the UserPassesTestMixin used to determine if a user has
# has the correct privileges to interact with Creation Views
class CreateCommon(UserPassesTestMixin, CreateView, ABC):

    # key is used to construct commonly formatted strings, such as used in the get_success_url
    key = None

    # this is where the user should be redirected if they're not logged in
    login_url = '/accounts/login_required/'

    # title to display on the CreateView page
    title = None

    # default template to use to create an update
    #  _entry_form.html contains the common navigation elements at the top of the template
    #  _entry_form_no_nav.html does not contain navigation at the top of the template
    template_name = 'shared_models/_entry_form.html'

    # an extending class can override this similarly to how the template_name attribute can be overriden
    # Except in this case the value will be used to include a java_script file at the bottom of the
    # 'shared_models/_entry_form.html' template
    java_script = None

    # an extending class can override this similarly to how the template_name attribute can be overriden
    # Except in this case the value will be used to include a nav_menu file at the top of the
    # 'shared_models/_entry_form.html' template
    nav_menu = None

    # an extending class can override this similarly to how the template_name attribute can be overriden
    # Except in this case the value will be used to include a site_css file at the top of the
    # 'shared_models/_entry_form.html' template
    site_css = None

    def get_title(self, **kwargs):
        if not self.title:
            raise AttributeError("No title attribute set in the class extending CreateCommon")

        return self.title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = self.get_title()

        context["auth"] = self.test_func()

        if self.java_script:
            context['java_script'] = self.java_script

        if self.nav_menu:
            context['nav_menu'] = self.nav_menu

        if self.site_css:
            context['site_css'] = self.site_css

        return context
