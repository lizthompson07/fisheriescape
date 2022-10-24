from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect

from herring.utils import can_read, is_admin, is_crud_user


class HerringBasicMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return can_read(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=herring')
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = is_admin(self.request.user)
        context["is_crud_user"] = is_crud_user(self.request.user)
        return context


class HerringAccess(HerringBasicMixin):
    pass


class HerringAdmin(HerringBasicMixin):
    def test_func(self):
        return is_admin(self.request.user)

class HerringCRUD(HerringBasicMixin):

    def test_func(self):
        return is_crud_user(self.request.user)



class SuperuserOrAdminRequiredMixin(HerringBasicMixin):

    def test_func(self):
        return self.request.user.is_superuser or is_admin(self.request.user)

