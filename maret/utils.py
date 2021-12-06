import requests
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse

from django.utils.translation import gettext_lazy as _

from shared_models import models as shared_models
from maret import models


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


def toggle_help_text_edit(request, user_id):
    usr = User.objects.get(pk=user_id)

    user_mode = None
    # mode 1 is read only
    mode = 1
    if models.UserMode.objects.filter(user=usr):
        user_mode = models.UserMode.objects.get(user=usr)
        mode = user_mode.mode

    # fancy math way of toggling between 1 and 2
    mode = (mode % 2) + 1

    if not user_mode:
        user_mode = models.UserMode(user=usr)

    user_mode.mode = mode
    user_mode.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def get_help_text_dict(model=None, title=''):
    my_dict = {}
    if not model:
        for obj in models.HelpText.objects.all():
            my_dict[obj.field_name] = str(obj)
    else:
        # If a model is supplied get the fields specific to that model
        for obj in models.HelpText.objects.filter(model=str(model.__name__)):
            my_dict[obj.field_name] = str(obj)

    return my_dict


def ajax_get_fields(request):
    model_name = request.GET.get('model', None)

    # use the model name passed from the web page to find the model in the apps models file
    model = models.__dict__[model_name]

    # use the retrieved model and get the doc string which is a string in the format
    # SomeModelName(id, field1, field2, field3)
    # remove the trailing parentheses, split the string up based on ', ', then drop the first element
    # which is the model name and the id.
    match = str(model.__dict__['__doc__']).replace(")", "").split(", ")[1:]
    fields = list()
    for f in match:
        label = "---"
        attr = getattr(model, f).field
        if hasattr(attr, 'verbose_name'):
            label = attr.verbose_name

        fields.append([f, label])

    data = {
        'fields': fields
    }

    return JsonResponse(data)


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
