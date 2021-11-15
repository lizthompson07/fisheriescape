from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

from diets.utils import is_crud_user, is_admin, can_read


class DietsBasicMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("accounts:denied_access"))
        return super().dispatch(request, *args, **kwargs)


class DietsAccessRequiredMixin(DietsBasicMixin):
    def test_func(self):
        return can_read(self.request.user)


class DietsCRUDRequiredMixin(DietsBasicMixin):
    def test_func(self):
        return is_crud_user(self.request.user)


class DietsAdminRequiredMixin(DietsBasicMixin):
    def test_func(self):
        return is_admin(self.request.user)


class SuperuserOrAdminRequiredMixin(DietsBasicMixin):
    def test_func(self):
        return self.request.user.is_superuser or is_admin(self.request.user)
