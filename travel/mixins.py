from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect

from travel import models
from travel.utils import in_travel_regional_admin_group, in_travel_nat_admin_group, can_modify_request, is_approver, is_admin


# This allows any logged in user to access the view
class TravelBasicMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login/'

    def test_func(self):
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_travel_regional_admin_group(self.request.user)
        context["is_adm_admin"] = in_travel_nat_admin_group(self.request.user)
        return context



class TravelAdminRequiredMixin(TravelBasicMixin):
    def test_func(self):
        return is_admin(self.request.user)


class TravelADMAdminRequiredMixin(TravelBasicMixin):
    def test_func(self):
        return in_travel_nat_admin_group(self.request.user)


class CanModifyMixin(TravelBasicMixin):
    def test_func(self):
        return can_modify_request(self.request.user, self.kwargs.get("pk"))


class AdminOrApproverRequiredMixin(TravelBasicMixin):

    def test_func(self):
        my_trip_request = models.TripRequest.objects.get(pk=self.kwargs.get("pk"))
        my_user = self.request.user
        if in_travel_regional_admin_group(my_user) or is_approver(my_user, my_trip_request):
            return True


# This allows any logged in user to access the view
class TravelAccessRequiredMixin(TravelBasicMixin):
    pass


class SuperuserOrNationalAdminRequiredMixin(TravelBasicMixin):

    def test_func(self):
        return self.request.user.is_superuser or in_travel_nat_admin_group(self.request.user)

