from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect

from grais.utils import is_grais_admin, has_grais_crud, has_grais_access


class GRAISBasicMixin(LoginRequiredMixin, UserPassesTestMixin):

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = is_grais_admin(self.request.user)
        return context


class GraisAccessRequiredMixin(GRAISBasicMixin):
    def test_func(self):
        return has_grais_access(self.request.user)


class GraisCRUDRequiredMixin(GRAISBasicMixin):
    def test_func(self):
        return has_grais_crud(self.request.user)


class GraisAdminRequiredMixin(GRAISBasicMixin):
    def test_func(self):
        return is_grais_admin(self.request.user)


class SuperuserOrAdminRequiredMixin(GRAISBasicMixin):
    def test_func(self):
        return self.request.user.is_superuser or is_grais_admin(self.request.user)
