from django.views.generic import TemplateView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.conf import settings

from django.urls import reverse_lazy
from django_filters.views import FilterView
from django.utils.translation import gettext_lazy as _

from . import forms, models, filters, utils

import json


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
                        'icon': "img/whalesdb/deployment.svg",
                    },
                    {
                        'title': _("Mooring Setup List"),
                        'url': "whalesdb:list_mor",
                        'icon': "img/whalesdb/mooring.svg",
                    },
                    {
                        'title': _("Project List"),
                        'url': "whalesdb:list_prj",
                        'icon': "img/whalesdb/project.svg",
                    },
                    {
                        'title': _("Station List"),
                        'url': "whalesdb:list_stn",
                        'icon': "img/whalesdb/station.svg",
                    },
                ]
            },
        ]
        context['auth'] = utils.whales_authorized(self.request.user)

        return context


class CreateCommon(UserPassesTestMixin, CreateView):
    # key is used to construct commonly formatted strings
    key = None

    # this is where the user should be redirected if they're not logged in
    login_url = '/accounts/login_required/'

    # default template to use to create an update
    template_name = 'whalesdb/_entry_form.html'

    # title to display on the CreateView page
    title = None

    def get_template_names(self):
        if self.kwargs.get("pop"):
            return 'whalesdb/_entry_form_no_nav.html'

        return self.template_name

    def get_success_url(self):
        success_url = reverse_lazy("whalesdb:list_{}".format(self.key))

        if self.kwargs.get("pop"):
            # create views are all intended to be pop out windows so upon success close the window
            success_url = reverse_lazy("shared_models:close_me_no_refresh")

        return success_url

    def test_func(self):
        return self.request.user.groups.filter(name='whalesdb_admin').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.title:
            context["title"] = self.title

        return context


class CreateDep(CreateCommon):
    key = 'dep'
    model = models.DepDeployment
    form_class = forms.DepForm
    title = _("Create Deployment")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        station_dict = [{"stn_id": v[0], "stn_code": v[2]} for v in
                        models.StnStation.objects.all().order_by('stn_id').values_list()]

        context['station_json'] = json.dumps(station_dict)

        return context


class CreateEmm(CreateCommon):
    key = 'emm'
    model = models.EmmMakeModel
    form_class = forms.EmmForm
    title = _("Create Make/Model")

    def form_valid(self, form):
        emm = form.save()

        if emm.eqt.pk == 4:
            return HttpResponseRedirect(reverse_lazy('whalesdb:details_emm', args=(emm.pk,)))
        else:
            return HttpResponseRedirect(self.get_success_url())


class CreateEqh(CreateCommon):
    key = 'eqh'
    model = models.EqhHydrophoneProperty
    form_class = forms.EqhForm
    title = _("Hydrophone Properties")

    def get_initial(self):
        initial = super().get_initial()
        initial['emm'] = self.kwargs['pk']

        return initial


class CreateEqp(CreateCommon):
    key = 'eqp'
    model = models.EqpEquipment
    form_class = forms.EqpForm
    title = _("Create Equipment")


class CreateEqo(CreateCommon):
    key = 'eqo'
    model = models.EqoOwner
    form_class = forms.EqoForm
    title = _("Create Equipment Owner")


class CreateMor(CreateCommon):
    key = 'mor'
    model = models.MorMooringSetup
    form_class = forms.MorForm
    title = _("Create Mooring Setup")


class CreatePrj(CreateCommon):
    key = 'prj'
    model = models.PrjProject
    form_class = forms.PrjForm
    title = _("Create Project")


class CreateSte(CreateCommon):
    key = 'ste'
    model = models.SteStationEvent
    form_class = forms.SteForm
    title = _("Create Station Event")

    def get_initial(self):
        init = super().get_initial()
        if 'dep_id' in self.kwargs and models.DepDeployment.objects.filter(pk=self.kwargs['dep_id']):
            init['dep'] = models.DepDeployment.objects.get(pk=self.kwargs['dep_id'])

        if 'set_id' in self.kwargs and models.SetStationEventCode.objects.filter(pk=self.kwargs['set_id']):
            init['set_type'] = models.SetStationEventCode.objects.get(pk=self.kwargs['set_id'])
        return init


class CreateStn(CreateCommon):
    key = 'stn'
    model = models.StnStation
    form_class = forms.StnForm
    title = _("Create Station")


class UpdateCommon(UserPassesTestMixin, UpdateView):
    # this is where the user should be redirected if they're not logged in
    login_url = '/accounts/login_required/'

    # default template to use to create an update
    template_name = 'whalesdb/_entry_form.html'

    # title to display on the CreateView page
    title = None

    # update views are all intended to be pop out windows so upon success close the window
    success_url = reverse_lazy("shared_models:close_me_no_refresh")

    def get_template_names(self):
        if self.kwargs.get("pop"):
            return 'whalesdb/_entry_form_no_nav.html'

        return self.template_name

    # this function overrides UserPassesTestMixin.test_func() to determine if
    # the user should have access to this content, if the user is logged in
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        station_dict = [{"stn_id": v[0], "stn_code": v[2]} for v in
                        models.StnStation.objects.all().order_by('stn_id').values_list()]

        context['station_json'] = json.dumps(station_dict)

        return context


class UpdateEmm(UpdateCommon):
    model = models.EmmMakeModel
    form_class = forms.EmmForm
    title = _("Update Make/Model")


class UpdateEqh(UpdateCommon):
    model = models.EqhHydrophoneProperty
    form_class = forms.EqhForm
    title = _("Hydrophone Properties")


class UpdateEqp(UpdateCommon):
    model = models.EqpEquipment
    form_class = forms.EqpForm
    title = _("Update Equipment")


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
    # default template to use to create a details view
    template_name = "whalesdb/whales_details.html"

    # title to display on the list page
    title = None

    # key used for creating default list and update URLs in the get_context_data method
    key = None

    # URL linking the details page back to the proper list
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
        context['auth'] = utils.whales_authorized(self.request.user)


        return context


class DetailsDep(DetailsCommon):
    key = "dep"
    model = models.DepDeployment
    template_name = 'whalesdb/details_dep.html'
    title = _("Deployment Details")
    fields = ['dep_name', 'dep_year', 'dep_month', 'stn', 'prj', 'mor']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['google_api_key'] = settings.GOOGLE_API_KEY

        return context


class DetailsEmm(DetailsCommon):
    key = "emm"
    model = models.EmmMakeModel
    template_name = 'whalesdb/emm_details.html'
    title = _("Make/Model Details")
    fields = ['eqt', 'emm_make', 'emm_model', 'emm_depth_rating', 'emm_description']


class DetailsEqp(DetailsCommon):
    key = "eqp"
    model = models.EqpEquipment
    title = _("Equipment Details")
    fields = ['emm', 'eqp_serial', 'eqp_asset_id', 'eqp_date_purchase', 'eqp_notes', 'eqp_retired', 'eqo_owned_by']


class DetailsMor(DetailsCommon):
    key = "mor"
    model = models.MorMooringSetup
    template_name = 'whalesdb/details_mor.html'
    title = _("Mooring Setup Details")
    fields = ["mor_name", "mor_max_depth", "mor_link_setup_image", "mor_additional_equipment",
              "mor_general_moor_description", "mor_notes"]
    creation_form_height = 600


class DetailsPrj(DetailsCommon):
    key = 'prj'
    model = models.PrjProject
    title = _("Project Details")
    fields = ['prj_name', 'prj_description', 'prj_url']
    creation_form_height = 725


class DetailsStn(DetailsCommon):
    key = 'stn'
    model = models.StnStation
    title = _("Station Details")
    template_name = 'whalesdb/details_stn.html'
    fields = ['stn_name', 'stn_code', 'stn_revision', 'stn_planned_lat', 'stn_planned_lon',
              'stn_planned_depth', 'stn_notes']
    creation_form_height = 400

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['google_api_key'] = settings.GOOGLE_API_KEY

        return context


class ListCommon(FilterView):
    # default template to use to create a filter view
    template_name = 'whalesdb/whale_filter.html'

    # title to display on the list page
    title = None

    # key used for creating default create, update and details URLs in the get_context_data method
    key = None

    # fields to be used as columns to display an object in the filter view table
    fields = []

    # URL to use to create a new object to be added to the filter view
    create_url = None

    # URL to use for the details button element in the filter view's list
    details_url = None

    # URL to use for the update button element in the filter view's list
    update_url = None

    # The height of the popup dialog used to display the creation/update form
    # if not set by the extending class the default popup height will be used
    creation_form_height = None

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, object_list=object_list, **kwargs)

        context['fields'] = self.fields

        if self.title:
            context['title'] = self.title

        context['create_url'] = self.create_url if self.create_url else "whalesdb:create_{}".format(self.key)
        context['details_url'] = self.details_url if self.details_url else "whalesdb:details_{}".format(self.key)
        context['update_url'] = self.update_url if self.update_url else "whalesdb:update_{}".format(self.key)

        context['auth'] = utils.whales_authorized(self.request.user)

        if self.creation_form_height:
            context['height'] = self.creation_form_height

        return context


class ListDep(ListCommon):
    key = 'dep'
    model = models.DepDeployment
    filterset_class = filters.DepFilter
    fields = ['dep_name', 'dep_year', 'dep_month', 'stn', 'prj', 'mor']
    title = _("Deployment List")
    creation_form_height = 600


class ListEmm(ListCommon):
    key = 'emm'
    model = models.EmmMakeModel
    filterset_class = filters.EmmFilter
    fields = ['eqt', 'emm_make', 'emm_model', 'emm_depth_rating']
    title = _("Make/Model List")


class ListEqp(ListCommon):
    key = 'eqp'
    model = models.EqpEquipment
    filterset_class = filters.EqpFilter
    fields = ['emm', 'eqp_serial', 'eqp_date_purchase', 'eqo_owned_by', 'eqp_retired', "eqp_deployed"]
    title = _("Equipment List")


class ListMor(ListCommon):
    key = 'mor'
    model = models.MorMooringSetup
    filterset_class = filters.MorFilter
    fields = ['mor_name', 'mor_max_depth', 'mor_notes']
    title = _("Mooring Setup List")
    creation_form_height = 725


class ListPrj(ListCommon):
    key = 'prj'
    model = models.PrjProject
    filterset_class = filters.PrjFilter
    title = _("Project List")
    fields = ['prj_name', 'prj_description']
    creation_form_height = 400


class ListStn(ListCommon):
    key = 'stn'
    model = models.StnStation
    filterset_class = filters.StnFilter
    fields = ['stn_name', 'stn_code', 'stn_revision']
    title = _("Station List")
