import requests
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse

from django.utils.translation import gettext_lazy as _

from shared_models import models as shared_models
from maret import models


class MaretBasicRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if self.request.user.id:
            return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_maret_admin_group(self.request.user)
        context["is_author"] = in_maret_author_group(self.request.user) or context["is_admin"]
        context["is_user"] = in_maret_user_group(self.request.user) or context["is_author"]
        return context


def in_maret_admin_group(user):
    if user:
        return bool(hasattr(user, "maret_user") and user.maret_user.is_admin)


def in_maret_author_group(user):
    if user:
        return bool(hasattr(user, "maret_user") and user.maret_user.is_author)


def in_maret_user_group(user):
    if user:
        return bool(hasattr(user, "maret_user") and user.maret_user.is_user)


class AdminOrSuperuserRequiredMixin(MaretBasicRequiredMixin):

    def test_func(self):
        return self.request.user.is_superuser or in_maret_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access', kwargs={
                "message": _("Sorry, you need to be a MarET admin in order to access this page.")}))
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(MaretBasicRequiredMixin):

    def test_func(self):
        return in_maret_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access', kwargs={
                "message": _("Sorry, you need to be a MarET admin in order to access this page.")}))
        return super().dispatch(request, *args, **kwargs)


class AuthorRequiredMixin(AdminRequiredMixin):

    def test_func(self):
        return super().test_func() or in_maret_author_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access', kwargs={
                "message": _("Sorry, you need to be a MarET Author in order to access this page.")}))
        return super().dispatch(request, *args, **kwargs)


class UserRequiredMixin(AuthorRequiredMixin):

    def test_func(self):
        return super().test_func() or in_maret_user_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access', kwargs={
                "message": _("Sorry, you need to be a MarET User in order to access this page.")}))
        return super().dispatch(request, *args, **kwargs)


def toggle_help_text_edit(request, user_id):
    usr = User.objects.get(pk=user_id)

    user_mode = None
    # mode 1 is read only
    mode = 1
    if models.MaretUser.objects.filter(user=usr):
        user_mode = models.MaretUser.objects.get(user=usr)
        mode = user_mode.mode

    # fancy math way of toggling between 1 and 2
    mode = (mode % 2) + 1

    if not user_mode:
        user_mode = models.MaretUser(user=usr)

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


def ajax_get_aops(request):
    # aops = area office programs
    area_office_id = request.GET.get('area_office', None)

    if area_office_id == '':
        aops = models.AreaOfficeProgram.objects.all()
    else:
        aops = models.AreaOfficeProgram.objects.filter(area_office__pk=area_office_id)

    fields = list(["{}:{}".format(aop.pk, str(aop)) for aop in aops])
    fields.insert(0, ":---------")
    data = {
        'area_office_program': fields
    }

    return JsonResponse(data)
