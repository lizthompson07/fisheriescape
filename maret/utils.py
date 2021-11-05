from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse

from django.utils.translation import gettext_lazy as _

from shared_models import models as shared_models


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return maret_admin_authorized(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access', kwargs={
                "message": _("Sorry, you need to be a MarET admin in order to access this page.")}))
        return super().dispatch(request, *args, **kwargs)


class AuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return maret_author_authorized(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access', kwargs={
                "message": _("Sorry, you need to be a MarET Author in order to access this page.")}))
        return super().dispatch(request, *args, **kwargs)


class UserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return maret_user_authorized(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access', kwargs={
                "message": _("Sorry, you need to be a MarET User in order to access this page.")}))
        return super().dispatch(request, *args, **kwargs)


# authorize for users who may view data only
def maret_user_authorized(user):
    return user.is_authenticated and user.groups.filter(name='maret_user').exists() or maret_author_authorized(user)


# authorize for users who may view and edit data
def maret_author_authorized(user):
    return user.is_authenticated and user.groups.filter(name='maret_author').exists() or maret_admin_authorized(user)


# authorize for administrators
def maret_admin_authorized(user):
    return user.is_authenticated and user.groups.filter(name='maret_admin').exists()


def ajax_get_divisions(request):
    branch_id = request.GET.get('branch', None)

    if branch_id == '':
        divisions = shared_models.Division.objects.all()
    else:
        divisions = shared_models.Division.objects.filter(branch__pk=branch_id)

    fields = list(["{}:{}".format(d.pk, str(d)) for d in divisions])
    fields.insert(0, ":---------")
    data = {
        'divisions': fields
    }

    return JsonResponse(data)
