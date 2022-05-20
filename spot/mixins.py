from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect

from spot.utils import is_admin, has_read_only


class SpotBasicMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return has_read_only(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=spot')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = is_admin(self.request.user)
        return context


class SpotAccessRequiredMixin(SpotBasicMixin):
    pass


class SpotAdminRequiredMixin(SpotBasicMixin):
    def test_func(self):
        return is_admin(self.request.user)


class SuperuserOrAdminRequiredMixin(SpotBasicMixin):
    def test_func(self):
        return self.request.user.is_superuser or is_admin(self.request.user)
