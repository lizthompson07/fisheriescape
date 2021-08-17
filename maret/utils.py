from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.utils.translation import gettext_lazy as _


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
