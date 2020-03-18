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
        context['auth'] = utils.whales_authorized(self.request.user)

        return context


# CommonCreate Extends the UserPassesTestMixin used to determine if a user has
# has the correct privileges to interact with Creation Views
class CommonCreate(UserPassesTestMixin, CreateView):

    # key is used to construct commonly formatted strings, such as used in the get_success_url
    key = None

    # this is where the user should be redirected if they're not logged in
    login_url = '/accounts/login_required/'

    # default template to use to create an update
    #  _entry_form.html contains the common navigation elements at the top of the template
    #  _entry_form_no_nav.html does not contain navigation at the top of the template
    template_name = 'whalesdb/_entry_form.html'

    # title to display on the CreateView page
    title = None

    # If a url is setup to use <str:pop> in its path, indicating the creation form is in a popup window
    # get_template_names will return the _entry_form_no_nav.html template.
    def get_template_names(self):
        if self.kwargs.get("pop"):
            return 'whalesdb/_entry_form_no_nav.html'

        return self.template_name

    # Upon success most creation views will be redirected to their respective 'CommonList' view. To send
    # a successful creation view somewhere else, override this method
    def get_success_url(self):
        success_url = reverse_lazy("whalesdb:list_{}".format(self.key))

        if self.kwargs.get("pop"):
            # create views intended to be pop out windows should close the window upon success
            success_url = reverse_lazy("shared_models:close_me_no_refresh")

        return success_url

    # overrides the UserPassesTestMixin test to check that a user belongs to the whalesdb_admin group
    def test_func(self):
        return self.request.user.groups.filter(name='whalesdb_admin').exists()

    # Get context returns elements used on the page. Make sure when extending to call
    # context = super().get_context_data(**kwargs) so that elements created in the parent
    # class are inherited by the extending class.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.title:
            # used as the title of the creation view. Called in the _entry_form and _entry_form_no_nav tempaltes
            context["title"] = self.title

        return context


class DepCreate(CommonCreate):
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


class EmmCreate(CommonCreate):
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


class EqhCreate(CommonCreate):
    key = 'eqh'
    model = models.EqhHydrophoneProperty
    form_class = forms.EqhForm
    title = _("Hydrophone Properties")

    def get_initial(self):
        initial = super().get_initial()
        initial['emm'] = self.kwargs['pk']

        return initial


class EqoCreate(CommonCreate):
    key = 'eqo'
    model = models.EqoOwner
    form_class = forms.EqoForm
    title = _("Create Equipment Owner")


class EqpCreate(CommonCreate):
    # This key is used by CommonCreate to create the 'whalesdb:list_eqp' name in the get_success_url method
    key = 'eqp'

    # The model this class uses
    model = models.EqpEquipment

    # The form class this model uses
    form_class = forms.EqpForm

    # the title to use on this views creation template
    title = _("Create Equipment")


class EqrCreate(CommonCreate):
    key = 'eqr'
    model = models.EqrRecorderProperties
    form_class = forms.EqrForm
    title = _("Recorder Properties")

    def get_initial(self):
        initial = super().get_initial()
        initial['emm'] = self.kwargs['pk']

        return initial


class MorCreate(CommonCreate):
    key = 'mor'
    model = models.MorMooringSetup
    form_class = forms.MorForm
    title = _("Create Mooring Setup")


class PrjCreate(CommonCreate):
    key = 'prj'
    model = models.PrjProject
    form_class = forms.PrjForm
    title = _("Create Project")


class SteCreate(CommonCreate):
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


class StnCreate(CommonCreate):
    key = 'stn'
    model = models.StnStation
    form_class = forms.StnForm
    title = _("Create Station")


class CommonUpdate(UserPassesTestMixin, UpdateView):
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


class DepUpdate(CommonUpdate):
    model = models.DepDeployment
    form_class = forms.DepForm
    title = _("Update Deployment")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        station_dict = [{"stn_id": v[0], "stn_code": v[2]} for v in
                        models.StnStation.objects.all().order_by('stn_id').values_list()]

        context['station_json'] = json.dumps(station_dict)

        return context


class EmmUpdate(CommonUpdate):
    model = models.EmmMakeModel
    form_class = forms.EmmForm
    title = _("Update Make/Model")


class EqhUpdate(CommonUpdate):
    model = models.EqhHydrophoneProperty
    form_class = forms.EqhForm
    title = _("Hydrophone Properties")


class EqpUpdate(CommonUpdate):
    model = models.EqpEquipment
    form_class = forms.EqpForm
    title = _("Update Equipment")


class EqrUpdate(CommonUpdate):
    model = models.EqrRecorderProperties
    form_class = forms.EqrForm
    title = _("Recorder Properties")


class MorUpdate(CommonUpdate):
    model = models.MorMooringSetup
    form_class = forms.MorForm
    title = _("Update Mooring Setup")


class PrjUpdate(CommonUpdate):
    model = models.PrjProject
    form_class = forms.PrjForm
    title = _("Update Project")


class StnUpdate(CommonUpdate):
    model = models.StnStation
    form_class = forms.StnForm
    title = _("Update Station")


class CommonDetails(DetailView):
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


class DepDetails(CommonDetails):
    key = "dep"
    model = models.DepDeployment
    template_name = 'whalesdb/details_dep.html'
    title = _("Deployment Details")
    fields = ['dep_name', 'dep_year', 'dep_month', 'stn', 'prj', 'mor']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['google_api_key'] = settings.GOOGLE_API_KEY

        return context


class EmmDetails(CommonDetails):
    key = "emm"
    model = models.EmmMakeModel
    template_name = 'whalesdb/details_emm.html'
    title = _("Make/Model Details")
    fields = ['eqt', 'emm_make', 'emm_model', 'emm_depth_rating', 'emm_description']


class EqpDetails(CommonDetails):
    key = "eqp"
    model = models.EqpEquipment
    title = _("Equipment Details")
    fields = ['emm', 'eqp_serial', 'eqp_asset_id', 'eqp_date_purchase', 'eqp_notes', 'eqp_retired', 'eqo_owned_by']


class MorDetails(CommonDetails):
    key = "mor"
    model = models.MorMooringSetup
    template_name = 'whalesdb/details_mor.html'
    title = _("Mooring Setup Details")
    fields = ["mor_name", "mor_max_depth", "mor_link_setup_image", "mor_additional_equipment",
              "mor_general_moor_description", "mor_notes"]
    creation_form_height = 600


class PrjDetails(CommonDetails):
    key = 'prj'
    model = models.PrjProject
    title = _("Project Details")
    fields = ['prj_name', 'prj_description', 'prj_url']
    creation_form_height = 725


class StnDetails(CommonDetails):
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


class CommonList(FilterView):
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


class DepList(CommonList):
    key = 'dep'
    model = models.DepDeployment
    filterset_class = filters.DepFilter
    fields = ['dep_name', 'dep_year', 'dep_month', 'stn', 'prj', 'mor']
    title = _("Deployment List")
    creation_form_height = 600


class EmmList(CommonList):
    key = 'emm'
    model = models.EmmMakeModel
    filterset_class = filters.EmmFilter
    fields = ['eqt', 'emm_make', 'emm_model', 'emm_depth_rating']
    title = _("Make/Model List")


class EqpList(CommonList):
    key = 'eqp'
    model = models.EqpEquipment
    filterset_class = filters.EqpFilter
    fields = ['emm', 'eqp_serial', 'eqp_date_purchase', 'eqo_owned_by', 'eqp_retired', "eqp_deployed"]
    title = _("Equipment List")


class MorList(CommonList):
    key = 'mor'
    model = models.MorMooringSetup
    filterset_class = filters.MorFilter
    fields = ['mor_name', 'mor_max_depth', 'mor_notes']
    title = _("Mooring Setup List")
    creation_form_height = 725


class PrjList(CommonList):
    key = 'prj'
    model = models.PrjProject
    filterset_class = filters.PrjFilter
    title = _("Project List")
    fields = ['prj_name', 'prj_description']
    creation_form_height = 400


class StnList(CommonList):
    key = 'stn'
    model = models.StnStation
    filterset_class = filters.StnFilter
    fields = ['stn_name', 'stn_code', 'stn_revision']
    title = _("Station List")
