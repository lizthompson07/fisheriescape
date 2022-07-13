from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect

from ihub.utils import in_ihub_admin_group, in_ihub_edit_group


class iHubBasicMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=ihub')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_ihub_admin_group(self.request.user)
        return context


class iHubEditRequiredMixin(iHubBasicMixin):

    def test_func(self):
        return in_ihub_edit_group(self.request.user)


class iHubAdminRequiredMixin(iHubBasicMixin):

    def test_func(self):
        return in_ihub_admin_group(self.request.user)


class SuperuserOrAdminRequiredMixin(iHubBasicMixin):

    def test_func(self):
        return self.request.user.is_superuser or in_ihub_admin_group(self.request.user)
