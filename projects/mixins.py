from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .utils import can_modify_project, is_project_lead, in_projects_admin_group, is_management_or_admin


class ProjectLeadRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        # the assumption is that either we are passing in a Project object or an object that has a project as an attribute
        try:
            obj = self.get_object()
        except AttributeError:
            project_id = self.kwargs.get("project")
        else:
            try:
                project_id = getattr(obj, "project").id
            except AttributeError:
                project_id = obj.id
        finally:
            return can_modify_project(self.request.user, project_id) or is_project_lead(self.request.user, project_id)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access'))
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_projects_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access', kwargs={
                "message": _("Sorry, you need to be a manager of this project in order to access this page.")}))
        return super().dispatch(request, *args, **kwargs)


class ManagerOrAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return is_management_or_admin(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access', kwargs={
                "message": _("Sorry, you need to be a manager of this project in order to access this page.")}))
        return super().dispatch(request, *args, **kwargs)


class CanModifyProjectRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        # the assumption is that either we are passing in a Project object or an object that has a project as an attribute
        try:
            obj = self.get_object()
        except AttributeError:
            project_id = self.kwargs.get("project")
        else:
            try:
                project_id = getattr(obj, "project").id
            except AttributeError:
                project_id = obj.id
        finally:
            return can_modify_project(self.request.user, project_id)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access'))
        return super().dispatch(request, *args, **kwargs)

