from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect

from cars.utils import is_national_admin, is_admin, is_regional_admin, can_modify_vehicle


class CarsBasicMixin(LoginRequiredMixin, UserPassesTestMixin):
    home_url_name = "cars:index"

    def test_func(self):
        if self.request.user.id:
            return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=cars')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = is_admin(self.request.user)
        context["bootstrap5"] = True
        context["sortable"] = False
        return context


class CarsNationalAdminRequiredMixin(CarsBasicMixin):
    def test_func(self):
        return is_national_admin(self.request.user)


class CarsRegionalAdminRequiredMixin(CarsBasicMixin):
    def test_func(self):
        return is_regional_admin(self.request.user)


class CarsAdminRequiredMixin(CarsBasicMixin):
    def test_func(self):
        return is_regional_admin(self.request.user) or is_national_admin(self.request.user)


class CanModifyVehicleRequiredMixin(CarsBasicMixin):
    def test_func(self):
        vehicle = self.get_object()
        return can_modify_vehicle(self.request.user, vehicle)


class CanModifyReservationRequiredMixin(CarsBasicMixin):
    def test_func(self):
        if is_admin(self.request.user):
            return True
        return self.get_object().primary_driver == self.request.user


class SuperuserOrAdminRequiredMixin(CarsBasicMixin):
    def test_func(self):
        return self.request.user.is_superuser or is_national_admin(self.request.user)
