from django.views.generic import TemplateView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin

from django.urls import reverse, reverse_lazy
from django_filters.views import FilterView
from django.utils.translation import gettext_lazy as _


from . import forms
from . import models
from . import filters


class IndexView(TemplateView):
    template_name = 'whalesdb/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['section'] = [
            {
                'title': 'Entry Forms',
                'forms': [
                    {
                        'title': _("Deployment List"),
                        'url': "whalesdb:list_dep",
                        'icon': "img/whales/deployment.svg",
                    },
                    {
                        'title': _("Mooring Setup List"),
                        'url': "whalesdb:list_mor",
                        'icon': "img/whales/mooring.svg",
                    },
                    {
                        'title': _("Project List"),
                        'url': "whalesdb:list_prj",
                        'icon': "img/whales/project.svg",
                    },
                    {
                        'title': _("Station List"),
                        'url': "whalesdb:list_stn",
                        'icon': "img/whales/station.svg",
                    },
                ]
           },
        ]

        return context


class CloserTemplateView(TemplateView):
    template_name = 'whalesdb/close_me.html'


class CloserNoRefreshTemplateView(TemplateView):
    template_name = 'whalesdb/close_me_no_refresh.html'


class CreateCommon(UserPassesTestMixin, CreateView):
    login_url = '/accounts/login_required/'
    title = None
    # create views are all intended to be pop out windows so upon success close the window
    success_url = reverse_lazy("whalesdb:close_me")
    template_name = 'whalesdb/_entry_form.html'

    def test_func(self):
        return self.request.user.groups.filter(name='whalesdb_admin').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.title:
            context["title"] = self.title

        return context

    def form_invalid(self, form):
        invalid = super().form_valid(form)

        return invalid

    def form_valid(self, form):
        valid = super().form_valid(form)

        return valid


class CreateDep(CreateCommon):
    model = models.DepDeployment
    form_class = forms.DepForm
    title = _("Create Deployment")


class CreateMor(CreateCommon):
    model = models.MorMooringSetup
    form_class = forms.MorForm
    title = _("Create Mooring Setup")

    def form_valid(self, form):
        valid = super().form_valid(form)

        return valid


class CreatePrj(CreateCommon):
    model = models.PrjProject
    form_class = forms.PrjForm
    title = _("Create Project")


class CreateStn(CreateCommon):
    model = models.StnStation
    form_class = forms.StnForm
    title = _("Create Station")


class UpdateCommon(UserPassesTestMixin, UpdateView):
    login_url = '/accounts/login_required/'
    title = None
    # create views are all intended to be pop out windows so upon success close the window
    success_url = reverse_lazy("whalesdb:close_me")
    template_name = 'whalesdb/_entry_form.html'

    def test_func(self):
        return self.request.user.groups.filter(name='whalesdb_admin').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.title:
            context["title"] = self.title

        return context


class UpdateDep(UpdateCommon):
    model = models.DepDeployment
    form_class = forms.DepForm

    title = _("Update Deployment")


class UpdateMor(UpdateCommon):
    model = models.MorMooringSetup
    form_class = forms.MorForm

    title = _("Update Mooring Setup")


class UpdatePrj(UpdateCommon):
    model = models.PrjProject
    form_class = forms.PrjForm

    title = _("Update Project")


class UpdateStn(UpdateCommon):
    model = models.StnStation
    form_class = forms.StnForm

    title = _("Update Station")


class DetailsCommon(DetailView):
    key = None
    title = None
    template_name = "whalesdb/whales_details.html"
    list_url = None
    update_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.title:
            context['title'] = self.title

        if self.fields:
            context['fields'] = self.fields

        context['list_url'] = self.list_url if self.list_url else "whalesdb:list_{}".format(self.key)
        context['update_url'] = self.update_url if self.update_url else "whalesdb:update_{}".format(self.key)

        return context


class DetailsDep(DetailsCommon):
    key = "dep"
    model = models.DepDeployment
    template_name = 'whalesdb/depdeployment_details.html'
    title = _("Deployment Details")
    fields = ['dep_name', 'dep_year', 'dep_month', 'stn', 'prj', 'mor']


class DetailsMor(DetailsCommon):
    key = "mor"
    model = models.MorMooringSetup
    template_name = 'whalesdb/mormooringsetup_details.html'
    title = _("Mooring Setup Details")
    fields = ["mor_name", "mor_max_depth", "mor_link_setup_image", "mor_additional_equipment",
              "mor_general_moor_description", "mor_notes"]


class DetailsPrj(DetailsCommon):
    key = 'prj'
    model = models.PrjProject
    title = _("Project Details")
    fields = ['prj_name', 'prj_description', 'prj_url']


class DetailsStn(DetailsCommon):
    key = 'stn'
    model = models.StnStation
    title = _("Station Details")
    template_name = 'whalesdb/stnstation_details.html'
    fields = ['stn_name', 'stn_code', 'stn_revision', 'stn_planned_lat', 'stn_planned_lon',
              'stn_planned_depth', 'stn_notes']


class ListCommon(FilterView):
    template_name = 'whalesdb/whale_filter.html'
    key = None
    fields = []
    create_url = None
    details_url = None
    update_url = None
    title = None

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, object_list=object_list, **kwargs)

        context['fields'] = self.fields

        if self.title:
            context['title'] = self.title

        context['create_url'] = self.create_url if self.create_url else "whalesdb:create_{}".format(self.key)
        context['details_url'] = self.details_url if self.details_url else "whalesdb:details_{}".format(self.key)
        context['update_url'] = self.update_url if self.update_url else "whalesdb:update_{}".format(self.key)

        context['auth'] = self.request.user.is_authenticated and \
                          self.request.user.groups.filter(name='whalesdb_admin').exists()

        return context


class ListDep(ListCommon):
    key = 'dep'
    model = models.DepDeployment
    filterset_class = filters.DepFilter
    fields = ['dep_name', 'dep_year', 'dep_month', 'stn', 'prj', 'mor']
    title = _("Deployment List")


class ListMor(ListCommon):
    key = 'mor'
    model = models.MorMooringSetup
    filterset_class = filters.MorFilter
    fields = ['mor_name', 'mor_max_depth', 'mor_notes']
    title = _("Mooring Setup List")


class ListPrj(ListCommon):
    key = 'prj'
    model = models.PrjProject
    filterset_class = filters.PrjFilter
    title = _("Project List")
    fields = ['prj_name', 'prj_description']


class ListStn(ListCommon):
    key ='stn'
    model = models.StnStation
    filterset_class = filters.StnFilter
    fields = ['stn_name', 'stn_code', 'stn_revision']
    title = _("Station List")


