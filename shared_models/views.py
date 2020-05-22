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
from .mixins import CommonMixin, CommonFormMixin, CommonListMixin


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


class CommonTemplateView(TemplateView, CommonMixin):
    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        context.update(super().get_common_context())
        return context


# CommonCreate Extends the UserPassesTestMixin used to determine if a user has
# has the correct privileges to interact with Creation Views
class CommonCreateView(CreateView, CommonFormMixin):
    # default template to use to create an update
    #  shared_entry_form.html contains the common navigation elements at the top of the template
    template_name = 'shared_models/shared_entry_form.html'

    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        context.update(super().get_common_context())
        return context


# UpdateCreate Extends the UserPassesTestMixin used to determine if a user has
# has the correct privileges to interact with Creation Views
class CommonUpdateView(UpdateView, CommonFormMixin):
    # this is where the user should be redirected if they're not logged in
    login_url = '/accounts/login_required/'

    # default template to use to update an update
    #  shared_entry_form.html contains the common navigation elements at the top of the template
    template_name = 'shared_models/shared_entry_form.html'

    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        context.update(super().get_common_context())
        return context


class CommonFilterView(FilterView, CommonListMixin):
    # this is where the user should be redirected if they're not logged in
    login_url = '/accounts/login_required/'

    # default template to use to update an update
    #  shared_entry_form.html contains the common navigation elements at the top of the template
    template_name = 'shared_models/shared_entry_form.html'

    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        context.update(super().get_common_context())
        return context


class CommonListView(ListView, CommonListMixin):
    # this is where the user should be redirected if they're not logged in
    login_url = '/accounts/login_required/'

    # default template to use to update an update
    #  shared_entry_form.html contains the common navigation elements at the top of the template
    template_name = 'shared_models/shared_entry_form.html'

    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        context.update(super().get_common_context())
        return context


class CommonFormView(FormView, CommonFormMixin):

    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        context.update(super().get_common_context())
        return context


class CommonFormsetView(TemplateView, CommonFormMixin):
    queryset = None
    formset_class = None
    success_url = None
    home_url_name = None
    delete_url_name = None
    pre_display_fields = ["id", ]
    post_display_fields = None
    random_object = None

    # override this if there are authorization requirements
    def get_queryset(self):
        return self.queryset

    def get_success_url(self):
        return self.success_url

    def get_pre_display_fields(self):
        return self.pre_display_fields

    def get_post_display_fields(self):
        return self.post_display_fields

    def get_random_object(self):
        if self.random_object:
            return self.random_object
        else:
            return self.get_queryset().first()

    def test_func(self):
        return self.auth

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['random_object'] = self.get_random_object()
        context['delete_url_name'] = self.delete_url_name
        context['container_class'] = self.container_class

        # overwrite the existing field list to take just the fields being passed in by the formset / form
        context["field_list"] = [f for f in self.formset_class.form.base_fields]
        context["pre_display_fields"] = self.get_pre_display_fields()
        context["post_display_fields"] = self.get_post_display_fields()
        return context

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        formset = self.formset_class(queryset=queryset.all())
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        formset = self.formset_class(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(self.request, "Items have been successfully updated")
            return HttpResponseRedirect(self.get_success_url())
            # return self.form_valid(formset)
        else:
            return self.render_to_response(self.get_context_data(formset=formset))


class CommonHardDeleteView(View, SingleObjectMixin, ABC):
    '''a dangerous view; to use when you want to delete an object without any confirmation page; WARNING, this deletes on a GET request!!'''
    success_url = None

    def get(self, request, *args, **kwargs):
        my_obj = self.get_object()
        my_obj.delete()
        messages.error(self.request, f"{my_obj} has been successfully deleted.")

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")


#
##
###
####
######
####################  SOME COMMON FORMS

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
