from abc import ABC

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView
from django_filters.views import FilterView

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


class CommonCommon():
    # key is used to construct commonly formatted strings, such as used in the get_success_url
    key = None

    # title to display on the CreateView page
    title = None

    # an extending class can override this similarly to how the template_name attribute can be overriden
    # Except in this case the value will be used to include a java_script file at the bottom of the
    # 'shared_models/shared_entry_form.html' template
    java_script = None

    # an extending class can override this similarly to how the template_name attribute can be overriden
    # Except in this case the value will be used to include a nav_menu file at the top of the
    # 'shared_models/shared_entry_form.html' template
    nav_menu = None

    # an extending class can override this similarly to how the template_name attribute can be overriden
    # Except in this case the value will be used to include a site_css file at the top of the
    # 'shared_models/shared_entry_form.html' template
    site_css = None

    def get_title(self):
        if not self.title:
            raise AttributeError("No title attribute set in the class extending CreateCommon")

        return self.title

    # Can be overriden in the extending class to do things based on the kwargs passed in from get_context_data
    def get_java_script(self):
        return self.java_script

    # Can be overriden in the extending class to do things based on the kwargs passed in from get_context_data
    def get_nav_menu(self):
        return self.nav_menu

    # Can be overriden in the extending class to do things based on the kwargs passed in from get_context_data
    def get_site_css(self):
        return self.site_css

    def get_common_context(self) -> dict:
        context = dict()

        context["title"] = self.get_title()
        java_script = self.get_java_script()
        nav_menu = self.get_nav_menu()
        site_css = self.get_site_css()

        if java_script:
            context['java_script'] = java_script

        if nav_menu:
            context['nav_menu'] = nav_menu

        if site_css:
            context['site_css'] = site_css

        return context


# CommonCreate Extends the UserPassesTestMixin used to determine if a user has
# has the correct privileges to interact with Creation Views
class CreateCommon(UserPassesTestMixin, CreateView, CommonCommon, ABC):

    # this is where the user should be redirected if they're not logged in
    login_url = '/accounts/login_required/'

    # default template to use to create an update
    #  shared_entry_form.html contains the common navigation elements at the top of the template
    template_name = 'shared_models/shared_entry_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["auth"] = self.test_func()

        context.update(super().get_common_context())

        return context


# UpdateCreate Extends the UserPassesTestMixin used to determine if a user has
# has the correct privileges to interact with Creation Views
class UpdateCommon(UserPassesTestMixin, UpdateView, CommonCommon, ABC):

    # this is where the user should be redirected if they're not logged in
    login_url = '/accounts/login_required/'

    # default template to use to update an update
    #  shared_entry_form.html contains the common navigation elements at the top of the template
    template_name = 'shared_models/shared_entry_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["auth"] = self.test_func()

        context.update(super().get_common_context())

        return context


class FilterCommon(FilterView, CommonCommon):

    auth = True

    template_name = 'shared_models/shared_filter.html'

    # override this if there are authorization requirements
    def test_func(self):
        return self.auth

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, object_list=object_list, **kwargs)

        # for the most part if the user is authorized then the content is editable
        # but extending classes can choose to make content not editable even if the user is authorized
        # Default behaviour for the FilterCommon class is that users are authorized by default to view
        # Data, but not to create or modify it.
        context['auth'] = self.test_func()
        context['editable'] = context['auth']

        context.update(super().get_common_context())

        return context
