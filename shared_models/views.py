from abc import ABC

from django.utils.translation import gettext as _
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


class IndexTemplateView(TemplateView):
    template_name = 'shared_models/pop_index.html'


# SECTION #
###########

class SectionListView(LoginRequiredMixin, FilterView):
    model = models.Section
    template_name = 'shared_models/generic_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Sections")
        context["field_list"] = [
            "tname|{}".format(_("name")),
            "abbrev",
            "region",
            "division",
            "branch",
            "head",
            "date_last_modified",
            "last_modified_by",
        ]
        context["random_object"] = self.object_list.first()
        context["model_name"] = "section"
        return context


class SectionUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Section
    template_name = 'shared_models/generic_form.html'
    form_class = forms.SectionForm

    def get_initial(self):
        return {"last_modified_by": self.request.user, }

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse_lazy('shared_models:section_list'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Section:")
        context["model_name"] = "section"
        return context


class SectionCreateView(LoginRequiredMixin, CreateView):
    model = models.Section
    template_name = 'shared_models/generic_form.html'
    form_class = forms.SectionForm

    def get_initial(self):
        return {"last_modified_by": self.request.user, }

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse_lazy('shared_models:section_list'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("New Section")
        context["model_name"] = "section"
        return context


class SectionDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Section
    success_url = reverse_lazy('shared_models:section_list')
    template_name = 'shared_models/generic_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Delete Section:")
        context["model_name"] = "section"
        context["related_names"] = {
            "project planning projects": getattr(self.get_object(), "projects").all(),
            "project planning functional groups": getattr(self.get_object(), "functional_groups").all(),
            "metadata resources": getattr(self.get_object(), "resources").all(),
            "travel trip requests": getattr(self.get_object(), "trip_requests").all(),
            "DM tickets": getattr(self.get_object(), "ticket_set").all(),
            "user profiles": getattr(self.get_object(), "profile_set").all(),
        }
        return context


# DIVISION #
############
class DivisionListView(LoginRequiredMixin, FilterView):
    model = models.Division
    template_name = 'shared_models/generic_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Divisions")
        context["field_list"] = [
            "tname|{}".format(_("name")),
            "abbrev",
            "division",
            "region",
            "head",
            "date_last_modified",
            "last_modified_by",
        ]
        context["random_object"] = self.object_list.first()
        context["model_name"] = "division"
        return context


class DivisionUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Division
    template_name = 'shared_models/generic_form.html'
    form_class = forms.DivisionForm

    def get_initial(self):
        return {"last_modified_by": self.request.user, }

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse_lazy('shared_models:division_list'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Division:")
        context["model_name"] = "division"
        return context


class DivisionCreateView(LoginRequiredMixin, CreateView):
    model = models.Division
    template_name = 'shared_models/generic_form.html'
    form_class = forms.DivisionForm

    def get_initial(self):
        return {"last_modified_by": self.request.user, }

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse_lazy('shared_models:division_list'))


class DivisionDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Division
    success_url = reverse_lazy('shared_models:division_list')
    template_name = 'shared_models/generic_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Delete Division:")
        context["model_name"] = "division"
        context["related_names"] = {
            "sections": getattr(self.get_object(), "sections").all(),
        }
        return context


# BRANCH #
##########
class BranchListView(LoginRequiredMixin, FilterView):
    model = models.Branch
    template_name = 'shared_models/generic_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Branches")
        context["field_list"] = [
            "tname|{}".format(_("name")),
            "abbrev",
            "region",
            "head",
            "date_last_modified",
            "last_modified_by",
        ]
        context["random_object"] = self.object_list.first()
        context["model_name"] = "branch"
        return context


class BranchUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Branch
    template_name = 'shared_models/generic_form.html'
    form_class = forms.BranchForm

    def get_initial(self):
        return {"last_modified_by": self.request.user, }

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse_lazy('shared_models:branch_list'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Branch:")
        context["model_name"] = "branch"
        return context


class BranchCreateView(LoginRequiredMixin, CreateView):
    model = models.Branch
    template_name = 'shared_models/generic_form.html'
    form_class = forms.BranchForm

    def get_initial(self):
        return {"last_modified_by": self.request.user, }

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse_lazy('shared_models:branch_list'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("New Branch")
        context["model_name"] = "branch"
        return context


class BranchDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Branch
    success_url = reverse_lazy('shared_models:branch_list')
    template_name = 'shared_models/generic_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Delete Division:")
        context["model_name"] = "division"
        context["related_names"] = {
            "divisions": getattr(self.get_object(), "divisions").all(),
        }
        return context

# REGION #
###########

class RegionListView(LoginRequiredMixin, FilterView):
    model = models.Region
    template_name = 'shared_models/generic_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Regions")
        context["field_list"] = [
            "tname|{}".format(_("name")),
            "abbrev",
            "head",
            "date_last_modified",
            "last_modified_by",
        ]
        context["random_object"] = self.object_list.first()
        context["model_name"] = "region"
        return context


class RegionUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Region
    template_name = 'shared_models/generic_form.html'
    form_class = forms.RegionForm

    def get_initial(self):
        return {"last_modified_by": self.request.user, }

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse_lazy('shared_models:section_list'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Region:")
        context["model_name"] = "region"
        return context


class RegionCreateView(LoginRequiredMixin, CreateView):
    model = models.Region
    template_name = 'shared_models/generic_form.html'
    form_class = forms.RegionForm

    def get_initial(self):
        return {"last_modified_by": self.request.user, }

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse_lazy('shared_models:region_list'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("New Region")
        context["model_name"] = "region"
        return context


class RegionDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Region
    success_url = reverse_lazy('shared_models:section_list')
    template_name = 'shared_models/generic_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Delete Region:")
        context["model_name"] = "region"
        context["related_names"] = {
            "branches": getattr(self.get_object(), "branches").all(),
            "cosignee codes": getattr(self.get_object(), "cosigneecode_set").all(),
            "trip meeting leads": getattr(self.get_object(), "meeting_leads").all(),
            "trip requests": getattr(self.get_object(), "trip_requests").all(),
        }
        return context

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
