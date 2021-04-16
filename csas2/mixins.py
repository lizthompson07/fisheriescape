from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import models, utils
from .utils import in_csas_crud_group, in_csas_admin_group

class LoginAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if self.request.user.id:
            return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class CsasAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return in_csas_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)



class CanModifyRequestRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        # the assumption is that either we are passing in a Project object or an object that has a project as an attribute
        project_id = None
        try:
            obj = self.get_object()
            if isinstance(obj, models.CSASRequest):
                request_id = obj.id

        except AttributeError:
            pass
            # if self.kwargs.get("project"):
            #     project_id = self.kwargs.get("project")
            # elif self.kwargs.get("project_year"):
            #     project_year = get_object_or_404(models.ProjectYear, pk=self.kwargs.get("project_year"))
            #     project_id = project_year.project_id

        finally:
            if project_id:
                return utils.can_modify_request(self.request.user, request_id)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access'))
        return super().dispatch(request, *args, **kwargs)
