from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _

from . import models
from .utils import can_modify_project, is_project_lead, in_ppt_admin_group, is_management_or_admin, in_ppt_national_admin_group


class PPTLoginRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_ppt_admin_group(self.request.user)
        return context


class ProjectLeadRequiredMixin(PPTLoginRequiredMixin):
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
            return can_modify_project(self.request.user, project_id=project_id) or is_project_lead(self.request.user, project_id)


class AdminRequiredMixin(PPTLoginRequiredMixin):
    def test_func(self):
        return in_ppt_admin_group(self.request.user)



class SuperuserOrNationalAdminRequiredMixin(PPTLoginRequiredMixin):
    def test_func(self):
        return self.request.user.is_superuser or in_ppt_national_admin_group(self.request.user)


class ManagerOrAdminRequiredMixin(PPTLoginRequiredMixin):
    def test_func(self):
        return is_management_or_admin(self.request.user)


class CanModifyProjectRequiredMixin(PPTLoginRequiredMixin):
    def test_func(self):
        # the assumption is that either we are passing in a Project object or an object that has a project as an attribute
        project_id = None
        try:
            obj = self.get_object()
            if isinstance(obj, models.Project):
                project_id = obj.id
            elif isinstance(obj, models.ProjectYear):
                project_id = obj.project_id
            elif isinstance(obj, models.DMA):
                project_id = obj.project_id
            elif isinstance(obj, models.StatusReport):
                project_id = obj.project_year.project_id

        except AttributeError:
            if self.kwargs.get("project"):
                project_id = self.kwargs.get("project")
            elif self.kwargs.get("project_year"):
                project_year = get_object_or_404(models.ProjectYear, pk=self.kwargs.get("project_year"))
                project_id = project_year.project_id

        finally:
            if project_id:
                return can_modify_project(self.request.user, project_id)
