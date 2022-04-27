from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect

from .utils import in_scuba_crud_group, in_scuba_admin_group


class ScubaBasicMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if self.request.user.id:
            return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=scuba')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_scuba_admin_group(self.request.user)
        return context


class LoginAccessRequiredMixin(ScubaBasicMixin):
    pass


class ScubaCRUDAccessRequiredMixin(ScubaBasicMixin):
    def test_func(self):
        return in_scuba_crud_group(self.request.user)


class ScubaAdminRequiredMixin(ScubaBasicMixin):
    def test_func(self):
        return in_scuba_admin_group(self.request.user)


class SuperuserOrAdminRequiredMixin(ScubaBasicMixin):
    def test_func(self):
        return self.request.user.is_superuser or in_scuba_admin_group(self.request.user)
