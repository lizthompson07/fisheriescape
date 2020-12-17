from copy import deepcopy

from django.utils.translation import gettext as _, gettext_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import TextField, Value
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView
from django_filters.views import FilterView
from django.contrib.auth.models import User, Group

from shared_models.views import CommonFilterView, CommonCreateView, CommonDetailView, CommonUpdateView, \
    CommonDeleteView, CommonHardDeleteView, CommonFormsetView
from . import models
from . import forms
from . import filters


class CloserTemplateView(TemplateView):
    template_name = 'vault/close_me.html'


### Permissions ###


class VaultAccessRequired(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


def in_vault_admin_group(user):
    if "vault_admin" in [g.name for g in user.groups.all()]:
        return True


class VaultAdminAccessRequired(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_vault_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


def in_vault_edit_group(user):
    """this group includes the admin group so there is no need to add an admin to this group"""
    if user:
        if in_vault_admin_group(user) or user.groups.filter(name='vault_edit').count() != 0:
            return True


class VaultEditRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_vault_edit_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


@login_required(login_url='/accounts/login/')
def index(request):
    return render(request, 'vault/index.html')


@login_required(login_url='/accounts/login/')
@user_passes_test(in_vault_admin_group, login_url='/accounts/denied/')
def admin_tools(request):
    return render(request, 'vault/_admin.html')


## ADMIN USER ACCESS CONTROL ##


class UserListView(VaultAdminAccessRequired, CommonFilterView):
    template_name = "vault/user_list.html"
    filterset_class = filters.UserFilter
    home_url_name = "index"
    paginate_by = 25
    h1 = "Vault App User List"
    field_list = [
        {"name": 'first_name', "class": "", "width": ""},
        {"name": 'last_name', "class": "", "width": ""},
        {"name": 'email', "class": "", "width": ""},
        {"name": 'last_login|{}'.format(gettext_lazy("Last login to DM Apps")), "class": "", "width": ""},
    ]
    new_object_url = reverse_lazy("shared_models:user_new")

    def get_queryset(self):
        queryset = User.objects.order_by("first_name", "last_name").annotate(
            search_term=Concat('first_name', Value(""), 'last_name', Value(""), 'email', output_field=TextField())
        )
        if self.kwargs.get("vault"):
            queryset = queryset.filter(groups__name__icontains="vault").distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vault_admin"] = get_object_or_404(Group, name="vault_admin")
        context["vault_edit"] = get_object_or_404(Group, name="vault_edit")
        return context


@login_required(login_url='/accounts/login/')
@user_passes_test(in_vault_admin_group, login_url='/accounts/denied/')
def toggle_user(request, pk, type):
    my_user = User.objects.get(pk=pk)
    vault_admin = get_object_or_404(Group, name="vault_admin")
    vault_edit = get_object_or_404(Group, name="vault_edit")
    if type == "admin":
        # if the user is in the admin group, remove them
        if vault_admin in my_user.groups.all():
            my_user.groups.remove(vault_admin)
        # otherwise add them
        else:
            my_user.groups.add(vault_admin)
    elif type == "edit":
        # if the user is in the edit group, remove them
        if vault_edit in my_user.groups.all():
            my_user.groups.remove(vault_edit)
        # otherwise add them
        else:
            my_user.groups.add(vault_edit)
    return HttpResponseRedirect("{}#user_{}".format(request.META.get('HTTP_REFERER'), my_user.id))


## ADMIN FORMSETS ##

## INSTRUMENT TYPE ##


class InstrumentTypeHardDeleteView(VaultAdminAccessRequired, CommonHardDeleteView):
    model = models.InstrumentType
    success_url = reverse_lazy("vault:manage_instrument_type")


class InstrumentTypeFormsetView(VaultAdminAccessRequired, CommonFormsetView):
    template_name = 'vault/formset.html'
    h1 = "Manage Instrument Type"
    queryset = models.InstrumentType.objects.all()
    formset_class = forms.InstrumentTypeFormset
    success_url = reverse_lazy("vault:manage_instrument_type")
    home_url_name = "vault:index"
    delete_url_name = "vault:delete_instrument_type"

## INSTRUMENT ##


class InstrumentHardDeleteView(VaultAdminAccessRequired, CommonHardDeleteView):
    model = models.Instrument
    success_url = reverse_lazy("vault:manage_instrument")


class InstrumentFormsetView(VaultAdminAccessRequired, CommonFormsetView):
    template_name = 'vault/formset.html'
    h1 = "Manage Instrument"
    queryset = models.Instrument.objects.all()
    formset_class = forms.InstrumentFormset
    success_url = reverse_lazy("vault:manage_instrument")
    home_url_name = "vault:index"
    delete_url_name = "vault:delete_instrument"


## ORGANISATION ##


class OrganisationHardDeleteView(VaultAdminAccessRequired, CommonHardDeleteView):
    model = models.Organisation
    success_url = reverse_lazy("vault:manage_organisation")


class OrganisationFormsetView(VaultAdminAccessRequired, CommonFormsetView):
    template_name = 'vault/formset.html'
    h1 = "Manage Organisation"
    queryset = models.Organisation.objects.all()
    formset_class = forms.OrganisationFormset
    success_url = reverse_lazy("vault:manage_organisation")
    home_url_name = "vault:index"
    delete_url_name = "vault:delete_organisation"


## PLATFORM TYPE ##


class ObservationPlatformTypeHardDeleteView(VaultAdminAccessRequired, CommonHardDeleteView):
    model = models.ObservationPlatformType
    success_url = reverse_lazy("vault:manage_platform_type")


class ObservationPlatformTypeFormsetView(VaultAdminAccessRequired, CommonFormsetView):
    template_name = 'vault/formset.html'
    h1 = "Manage Platform Type"
    queryset = models.ObservationPlatformType.objects.all()
    formset_class = forms.ObservationPlatformTypeFormset
    success_url = reverse_lazy("vault:manage_platform_type")
    home_url_name = "vault:index"
    delete_url_name = "vault:delete_platform_type"

# #
# # # SPECIES #
# # ###########
# #
#


class SpeciesListView(VaultAccessRequired, CommonFilterView):
    template_name = "vault/list.html"
    filterset_class = filters.SpeciesFilter
    h1 = "Species List"
    home_url_name = "vault:index"
    row_object_url_name = "vault:species_detail"
    new_btn_text = "New Species"

    queryset = models.Species.objects.annotate(
        search_term=Concat('code', 'english_name', 'french_name', 'latin_name', 'id', output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'code', "class": "", "width": ""},
        {"name": 'french_name', "class": "", "width": ""},
        {"name": 'english_name', "class": "", "width": ""},
        {"name": 'latin_name', "class": "", "width": ""},
        {"name": 'vor_code', "class": "red-font", "width": ""},
        {"name": 'quebec_code', "class": "", "width": ""},
        {"name": 'aphia_code', "class": "", "width": ""},

    ]

    def get_new_object_url(self):
        return reverse("vault:species_new", kwargs=self.kwargs)


class SpeciesDetailView(VaultAdminAccessRequired, CommonDetailView):
    model = models.Species
    field_list = [
            'id',
            'code',
            'english_name',
            'french_name',
            'latin_name',
            'vor_code',
            'quebec_code',
            'maritimes_code',
            'aphia_id',
        ]
    home_url_name = "vault:index"
    parent_crumb = {"title": gettext_lazy("Species List"), "url": reverse_lazy("vault:species_list")}


class SpeciesUpdateView(VaultAdminAccessRequired, CommonUpdateView):
    model = models.Species
    form_class = forms.SpeciesForm
    template_name = 'vault/form.html'
    cancel_text = _("Cancel")
    home_url_name = "vault:index"

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Species record successfully updated for : {my_object}"))
        return HttpResponseRedirect(reverse("vault:species_detail", kwargs=self.kwargs))

    def get_active_page_name_crumb(self):
        my_object = self.get_object()
        return my_object

    def get_h1(self):
        my_object = self.get_object()
        return my_object

    def get_parent_crumb(self):
        return {"title": str(self.get_object()), "url": reverse_lazy("vault:species_detail", kwargs=self.kwargs)}

    def get_grandparent_crumb(self):
        kwargs = deepcopy(self.kwargs)
        del kwargs["pk"]
        return {"title": _("Species List"), "url": reverse("vault:species_list", kwargs=kwargs)}


class SpeciesCreateView(VaultAdminAccessRequired, CommonCreateView):
    model = models.Species
    form_class = forms.SpeciesForm
    template_name = 'vault/form.html'
    home_url_name = "vault:index"
    h1 = gettext_lazy("Add New Species")
    parent_crumb = {"title": gettext_lazy("Species List"), "url": reverse_lazy("vault:species_list")}

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Species record successfully created for : {my_object}"))
        return super().form_valid(form)


class SpeciesDeleteView(VaultAccessRequired, CommonDeleteView):
    model = models.Species
    permission_required = "__all__"
    success_url = reverse_lazy('vault:species_list')
    template_name = 'vault/confirm_delete.html'
    home_url_name = "vault:index"
    grandparent_crumb = {"title": gettext_lazy("Species List"), "url": reverse_lazy("vault:species_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("vault:species_detail", kwargs=self.kwargs)}
