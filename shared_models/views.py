from abc import ABC

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView, ListView, FormView
from django.views.generic.detail import SingleObjectMixin
from django_filters.views import FilterView

###
from . import models
from . import forms


class CloserTemplateView(TemplateView):
    template_name = 'shared_models/close_me.html'


class CloserNoRefreshTemplateView(TemplateView):
    template_name = 'shared_models/close_me_no_refresh.html'


def in_admin_group(user):
    """give a list of groups that would be allowed to access this form"""
    if user.id:
        if user.groups.filter(name='travel_admin').count() != 0 or \
                user.groups.filter(name='travel_adm_admin').count():
            return True


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class IndexTemplateView(AdminRequiredMixin, TemplateView):
    template_name = 'shared_models/pop_index.html'


# SECTION #
###########

class SectionListView(AdminRequiredMixin, ListView):
    queryset = models.Section.objects.order_by("division__branch__region", "division__branch", "division", "name")
    template_name = 'shared_models/generic_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Sections")
        context["field_list"] = [
            "region",
            "branch",
            "division",
            "tname|{}".format(_("section")),
            "abbrev",
            "head",
            "date_last_modified",
            "last_modified_by",
        ]
        context["random_object"] = self.object_list.first()
        context["model_name"] = "section"
        return context


class SectionUpdateView(AdminRequiredMixin, UpdateView):
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
        context["related_names"] = {
            "project planning projects": getattr(self.get_object(), "projects").all(),
            "project planning functional groups": getattr(self.get_object(), "functional_groups").all(),
            "metadata resources": getattr(self.get_object(), "resources").all(),
            "travel trip requests": getattr(self.get_object(), "trip_requests").all(),
            "DM tickets": getattr(self.get_object(), "ticket_set").all(),
            "user profiles": getattr(self.get_object(), "profile_set").all(),
        }
        return context


class SectionCreateView(AdminRequiredMixin, CreateView):
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


class SectionDeleteView(AdminRequiredMixin, DeleteView):
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
class DivisionListView(AdminRequiredMixin, ListView):
    model = models.Division
    template_name = 'shared_models/generic_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Divisions")
        context["field_list"] = [
            "region",
            "branch",
            "tname|{}".format(_("division")),
            "abbrev",
            "head",
            "date_last_modified",
            "last_modified_by",
        ]
        context["random_object"] = self.object_list.first()
        context["model_name"] = "division"
        return context


class DivisionUpdateView(AdminRequiredMixin, UpdateView):
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
        context["related_names"] = {
            "sections": getattr(self.get_object(), "sections").all(),
        }
        return context


class DivisionCreateView(AdminRequiredMixin, CreateView):
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
        context["title"] = _("New Division")
        context["model_name"] = "division"
        return context


class DivisionDeleteView(AdminRequiredMixin, DeleteView):
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
class BranchListView(AdminRequiredMixin, ListView):
    model = models.Branch
    template_name = 'shared_models/generic_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Branches")
        context["field_list"] = [
            "region",
            "tname|{}".format(_("branch")),
            "abbrev",
            "head",
            "date_last_modified",
            "last_modified_by",
        ]
        context["random_object"] = self.object_list.first()
        context["model_name"] = "branch"
        return context


class BranchUpdateView(AdminRequiredMixin, UpdateView):
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
        context["related_names"] = {
            "divisions": getattr(self.get_object(), "divisions").all(),
        }
        return context


class BranchCreateView(AdminRequiredMixin, CreateView):
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


class BranchDeleteView(AdminRequiredMixin, DeleteView):
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

class RegionListView(AdminRequiredMixin, ListView):
    model = models.Region
    template_name = 'shared_models/generic_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Regions")
        context["field_list"] = [
            "tname|{}".format(_("region")),
            "abbrev",
            "head",
            "date_last_modified",
            "last_modified_by",
        ]
        context["random_object"] = self.object_list.first()
        context["model_name"] = "region"
        return context


class RegionUpdateView(AdminRequiredMixin, UpdateView):
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
        context["related_names"] = {
            "branches": getattr(self.get_object(), "branches").all(),
            "cosignee codes": getattr(self.get_object(), "cosigneecode_set").all(),
            "trip meeting leads": getattr(self.get_object(), "meeting_leads").all(),
            "trip requests": getattr(self.get_object(), "trip_requests").all(),
        }
        return context


class RegionCreateView(AdminRequiredMixin, CreateView):
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


class RegionDeleteView(AdminRequiredMixin, DeleteView):
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

    # an extending class can override this similarly to how the template_name attribute can be overriden
    # Except in this case the value will be used to include a field_list in the context var
    field_list = None
    h1 = None
    subtitle = None
    h2 = None
    h3 = None
    crumbs = None
    container_class = "container"

    def get_title(self):
        if not self.title and not self.h1:
            raise AttributeError("No title attribute set in the class extending CommonCommon")

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

    # Can be overriden in the extending class to do things based on the kwargs passed in from get_context_data
    def get_field_list(self):
        return self.field_list

    def get_subtitle(self):
        return self.subtitle

    def get_h1(self):
        return self.h1

    def get_h2(self):
        return self.h2

    def get_h3(self):
        return self.h3

    def get_crumbs(self):
        return self.crumbs

    def get_container_class(self):
        return self.container_class

    def get_common_context(self) -> dict:
        context = dict()

        context["title"] = self.get_title()
        java_script = self.get_java_script()
        nav_menu = self.get_nav_menu()
        site_css = self.get_site_css()

        field_list = self.get_field_list()
        h1 = self.get_h1()
        h2 = self.get_h2()
        h3 = self.get_h3()
        subtitle = self.get_subtitle()
        crumbs = self.get_crumbs()
        container_class = self.get_container_class()

        if java_script:
            context['java_script'] = java_script

        if nav_menu:
            context['nav_menu'] = nav_menu

        if site_css:
            context['site_css'] = site_css

        if field_list:
            context['field_list'] = field_list

        if subtitle:
            context['subtitle'] = subtitle
        # if there is no subtitle, use the h1 as a default
        elif h1:
            context['subtitle'] = h1

        if h1:
            context['h1'] = h1

        if h2:
            context['h2'] = h2

        if h3:
            context['h3'] = h3

        if crumbs:
            context['crumbs'] = crumbs

        context['container_class'] = container_class

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


class FormsetCommon(TemplateView, CommonCommon):
    auth = True
    template_name = 'shared_models/shared_filter.html'
    queryset = None
    formset_class = None
    success_url_name = None
    home_url_name = None
    delete_url_name = None

    # override this if there are authorization requirements

    def get_crumbs(self):
        return [
            {"title": _("Home"), "url": reverse(self.home_url_name)},
            {"title": self.h1}
        ]

    def test_func(self):
        return self.auth

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # for the most part if the user is authorized then the content is editable
        # but extending classes can choose to make content not editable even if the user is authorized
        # Default behaviour for the FilterCommon class is that users are authorized by default to view
        # Data, but not to create or modify it.
        context['auth'] = self.test_func()
        context['editable'] = context['auth']
        context['random_object'] = self.queryset.first()
        context['delete_url_name'] = self.delete_url_name
        context['container_class'] = self.container_class

        context.update(super().get_common_context())
        # overwrite the existing field list to take just the fields being passed in by the formset / form
        context["field_list"] = [f for f in self.formset_class.form.base_fields]
        return context

    def get(self, request, *args, **kwargs):
        formset = self.formset_class(queryset=self.queryset.all())
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        formset = self.formset_class(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(self.request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse(self.success_url_name))
            # return self.form_valid(formset)
        else:
            return self.render_to_response(self.get_context_data(formset=formset))


class HardDeleteView(View, SingleObjectMixin):
    '''a dangerous view; to use when you want to delete an object without any confirmation page'''
    success_url = None

    def get(self, request, *args, **kwargs):
        my_obj = self.get_object()
        my_obj.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")