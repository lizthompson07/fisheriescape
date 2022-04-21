from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _

from .utils import is_nat_admin, is_regional_admin, is_admin, is_custodian_or_admin


class InventoryBasicMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_nat_admin"] = is_nat_admin(self.request.user)
        context["is_regional_admin"] = is_regional_admin(self.request.user)
        context["is_admin"] = is_admin(self.request.user)
        return context


class AdminRequiredMixin(InventoryBasicMixin):
    def test_func(self):
        return is_admin(self.request.user)


class NationalAdminRequiredMixin(InventoryBasicMixin):
    def test_func(self):
        return is_nat_admin(self.request.user)


class RegionalAdminRequiredMixin(InventoryBasicMixin):
    def test_func(self):
        return is_regional_admin(self.request.user)


class SuperuserOrAdminRequiredMixin(InventoryBasicMixin):
    def test_func(self):
        return self.request.user.is_superuser or is_nat_admin(self.request.user)


class CustodianRequiredMixin(InventoryBasicMixin):

    def test_func(self):
        return is_custodian_or_admin(self.request.user, self.kwargs["pk"])

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("accounts:denied_access", kwargs={
                "message": _("Sorry, only custodians and system administrators have access to this view.")}))
        return super().dispatch(request, *args, **kwargs)
