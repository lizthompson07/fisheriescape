from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.utils import timezone

from .utils import is_crud_user, is_admin


class ednaBasicMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if self.request.user.id:
            return True

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # just to be very sure they are interacting with the correct TZ
    #     timezone.activate(settings.TIME_ZONE)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=edna')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = is_admin(self.request.user)
        return context


class eDNACRUDAccessRequiredMixin(ednaBasicMixin):
    def test_func(self):
        return is_crud_user(self.request.user)


class eDNAAdminRequiredMixin(ednaBasicMixin):
    def test_func(self):
        return is_admin(self.request.user)


class SuperuserOrAdminRequiredMixin(ednaBasicMixin):

    def test_func(self):
        return self.request.user.is_superuser or is_admin(self.request.user)
