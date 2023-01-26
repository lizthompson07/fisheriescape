from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from . import models
from .utils import is_nat_admin, is_regional_admin, is_admin, can_modify


class InventoryBasicMixin(LoginRequiredMixin, UserPassesTestMixin):
    home_url_name = "inventory:index"

    def test_func(self):
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=inventory')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_nat_admin"] = is_nat_admin(self.request.user)
        context["is_regional_admin"] = is_regional_admin(self.request.user)
        context["is_admin"] = is_admin(self.request.user)
        context["mapbox_api_key"] = settings.MAPBOX_API_KEY
        context['now'] = timezone.now()
        context["published_records"] = models.Resource.objects.filter(fgp_publication_date__isnull=False).count()
        context["flagged_4_deletion"] = models.Resource.objects.filter(flagged_4_deletion=True).count()
        context["flagged_4_publication"] = models.Resource.objects.filter(flagged_4_publication=True).count()
        return context


class InventoryLoginRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return bool(self.request.user and self.request.user.id)


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


class CanModifyRequiredMixin(InventoryBasicMixin):

    def test_func(self):
        resource_id = None
        if self.kwargs.get("resource"):
            resource_id = self.kwargs.get("resource")
        else:
            obj = self.get_object()
            if obj._meta.model == models.Resource:
                resource_id = obj.id
            elif hasattr(obj, "resource"):
                resource_id = obj.resource_id

        if resource_id:
            return can_modify(self.request.user, resource_id)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("accounts:denied_access", kwargs={
                "message": _("Sorry, only custodians and system administrators have access to this view.")}) + "?app=inventory")
        return super().dispatch(request, *args, **kwargs)
