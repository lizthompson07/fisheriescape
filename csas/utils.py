from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

# Staff_Users group who can input New Request and New Contact
def csas_authorized(user):
    return user.is_authenticated and (user.groups.filter(name='csas_users').exists() or csas_admin(user))


# csas_admin group who can input New Request, New Contact, New Meeting and New Publication
def csas_admin(user):
    return user.is_authenticated and (user.groups.filter(name='csas_admin').exists() or csas_super(user))


# csas_admin group who can input New Request, New Contact, New Meeting and New Publication
# Plus they have rights to update lookup tables
def csas_super(user):
    return user.is_authenticated and user.groups.filter(name='csas_super').exists()


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return csas_super(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access', kwargs={
                "message": _("Sorry, you need to be a csas super user in order to access this page.")}))
        return super().dispatch(request, *args, **kwargs)
