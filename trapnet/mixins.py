from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect

from trapnet.utils import can_access, is_admin, is_crud_user


class TrapNetBasicMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return can_access(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=trapnet')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = is_admin(self.request.user)
        context["mapbox_api_key"] = settings.MAPBOX_API_KEY
        return context


class TrapNetCRUDRequiredMixin(TrapNetBasicMixin):
    def test_func(self):
        return is_crud_user(self.request.user)



class TrapNetAdminRequiredMixin(TrapNetBasicMixin):

    def test_func(self):
        return is_admin(self.request.user)


class SuperuserOrAdminRequiredMixin(TrapNetBasicMixin):

    def test_func(self):
        return self.request.user.is_superuser or is_admin(self.request.user)
