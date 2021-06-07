import datetime

from django.views.generic import DetailView, DeleteView
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor

from whalesdb import forms, models, filters, utils
from django.contrib.auth.mixins import UserPassesTestMixin
from shared_models.views import CommonTemplateView, CommonAuthCreateView, CommonAuthUpdateView, CommonAuthFilterView, \
    CommonHardDeleteView, CommonFormsetView, CommonFormView, CommonFormMixin

import json
import shared_models.models as shared_models
from .utils import AdminRequiredMixin
from . import mixins, reports


# def ecp_delete(request, emm, ecp):
#     if utils.whales_authorized(request.user):
#         ecp_channel = models.EcpChannelProperty.objects.get(eqr=emm, ecp_channel_no=ecp)
#         ehe_list = models.EheHydrophoneEvent.objects.filter(rec__emm=emm, ecp_channel_no=ecp)
#         for ehe in ehe_list:
#             ehe.delete()
#         ecp_channel.delete()
#         messages.success(request, _("The make/model channel has been successfully deleted."))
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#     else:
#         return HttpResponseRedirect(reverse_lazy('accounts:denied_access'))


def tea_delete(request, pk):
    user_test_result = utils.whales_authorized(request.user)
    if user_test_result and request.user.is_authenticated:
        tea = models.TeaTeamMember.objects.get(pk=pk)
        tea.delete()
        messages.success(request, _("The team member has been successfully removed."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    elif not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/?next={}'.format(reverse_lazy("whalesdb:delete_tea", args=[pk, ])))
    else:
        return HttpResponseRedirect('/accounts/denied/')


class ReportView(CommonFormView):
    nav_menu = 'whalesdb/base/whales_nav_menu.html'
    site_css = 'whalesdb/base/whales_css.css'
    title = _("Whale Equipment Metadata Database Reports")
    form_class = forms.ReportSearchForm
    template_name = 'whalesdb/whales_reports.html'

    def form_valid(self, form):
        report_choice = int(form.cleaned_data["report"])

        if report_choice == 1:
            return reports.report_deployment_summary(self.request.POST)

        return super().form_valid(form)


class IndexView(CommonTemplateView):
    nav_menu = 'whalesdb/base/whales_nav_menu.html'
    site_css = 'whalesdb/base/whales_css.css'
    title = _("Whale Equipment Metadata Database")
    template_name = 'whalesdb/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()

        # for the most part if the user is authorized then the content is editable
        # but extending classes can choose to make content not editable even if the user is authorized
        context['auth'] = context['editable'] = utils.whales_authorized(self.request.user)

        return context


# CommonCreate Extends the UserPassesTestMixin used to determine if a user has
# has the correct privileges to interact with Creation Views
class CommonCreate(CommonAuthCreateView):

    nav_menu = 'whalesdb/base/whales_nav_menu.html'
    site_css = 'whalesdb/base/whales_css.css'
    home_url_name = "whalesdb:index"

    def get_nav_menu(self):
        if self.kwargs.get("pop"):
            return None

        return self.nav_menu

    # Upon success most creation views will be redirected to their respective 'CommonList' view. To send
    # a successful creation view somewhere else, override this method
    def get_success_url(self):
        success_url = self.success_url if self.success_url else reverse_lazy("whalesdb:list_{}".format(self.key))

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
        context['editable'] = context['auth']
        context['help_text_dict'] = utils.get_help_text_dict(self.model)
        return context


class CruCreate(mixins.CruMixin, CommonCreate):
    pass


class DepCreate(mixins.DepMixin, CommonCreate):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        station_dict = [{"pk": v[0], "stn_code": v[2]} for v in
                        models.StnStation.objects.all().order_by('pk').values_list()]

        context['station_json'] = json.dumps(station_dict)
        context['java_script'] = 'whalesdb/_entry_dep_js.html'

        return context


class EccCreate(mixins.EccMixin, CommonCreate):

    def get_initial(self):
        initial = super().get_initial()
        initial['eca'] = self.kwargs['eca']

        return initial


class EcaCreate(mixins.EcaMixin, CommonCreate):
    pass


class EcpCreate(mixins.EcpMixin, CommonCreate):

    def get_initial(self):
        initial = super().get_initial()
        initial['eqr'] = self.kwargs['eqr']

        return initial


class EdaCreate(mixins.EdaMixin, CommonCreate):

    def get_initial(self):
        initial = super().get_initial()
        initial['dep'] = self.kwargs['dep']

        return initial


class EmmCreate(mixins.EmmMixin, CommonCreate):

    def form_valid(self, form):
        emm = form.save()

        if emm.eqt.pk == 4:
            return HttpResponseRedirect(reverse_lazy('whalesdb:details_emm', args=(emm.pk,)))
        else:
            return HttpResponseRedirect(self.get_success_url())


class EheCreate(mixins.EheMixin, CommonCreate):

    def get_initial(self):
        initial = super().get_initial()
        initial['rec'] = self.kwargs['rec']
        initial['ecp_channel_no'] = self.kwargs['ecp_channel_no']
        initial['ehe_date'] = datetime.date.today()

        return initial

    def form_valid(self, form):
        data = form.cleaned_data
        # if any copy channel checks are checked then the even will be copied to all additional channels.
        for channel in data['copy_to_channel']:
            n_obj = models.EheHydrophoneEvent(ehe_date=data['ehe_date'], hyd=data['hyd'],
                                              rec=data['rec'], ecp_channel_no=channel)
            n_obj.save()

        return super().form_valid(form)


class EqhCreate(mixins.EqhMixin, CommonCreate):

    def get_initial(self):
        initial = super().get_initial()
        initial['emm'] = self.kwargs['pk']

        return initial


class EqoCreate(mixins.EqoMixin, CommonCreate):
    pass


class EqpCreate(mixins.EqpMixin, CommonCreate):
    pass


class EqrCreate(mixins.EqrMixin, CommonCreate):

    def get_initial(self):
        initial = super().get_initial()
        initial['emm'] = self.kwargs['pk']

        return initial


class EtrCreate(mixins.EtrMixin, CommonCreate):
    pass


class MorCreate(mixins.MorMixin, CommonCreate):
    pass


class PrjCreate(mixins.PrjMixin, CommonCreate):
    pass


class RciCreate(mixins.RciMixin, CommonCreate):

    def get_initial(self):
        init = super().get_initial()
        if 'rec_id' in self.kwargs and models.RecDataset.objects.filter(pk=self.kwargs['rec_id']):
            init['rec_id'] = models.RecDataset.objects.get(pk=self.kwargs['rec_id'])

        return init


class RecCreate(mixins.RecMixin, CommonCreate):

    def get_initial(self):
        init = super().get_initial()
        if 'eda' in self.kwargs and models.EdaEquipmentAttachment.objects.filter(pk=self.kwargs['eda']):
            init['eda_id'] = models.EdaEquipmentAttachment.objects.get(pk=self.kwargs['eda'])

        return init

    def get_success_url(self):
        if self.kwargs.get("eda"):
            eda = models.EdaEquipmentAttachment.objects.get(pk=self.kwargs['eda'])
            return reverse_lazy("whalesdb:details_dep", args=(eda.dep.pk,))

        return super().get_success_url()


class ReeCreate(mixins.ReeMixin, CommonCreate):

    def get_initial(self):
        init = super().get_initial()
        if 'rec_id' in self.kwargs and models.RecDataset.objects.filter(pk=self.kwargs['rec_id']):
            init['rec_id'] = models.RecDataset.objects.get(pk=self.kwargs['rec_id'])

        return init


class RetCreate(mixins.RetMixin, CommonCreate):
    pass


class RscCreate(mixins.RscMixin, CommonCreate):

    def form_valid(self, form):
        obj = form.save()

        return HttpResponseRedirect(reverse_lazy("whalesdb:details_rsc", kwargs={"pk": obj.pk}))


class RstCreate(mixins.RstMixin, CommonCreate):

    def get_initial(self):
        initial = super().get_initial()
        initial['rsc'] = self.kwargs['rsc']

        return initial


class SteCreate(mixins.SteMixin, CommonCreate):

    def get_initial(self):
        init = super().get_initial()
        if 'dep_id' in self.kwargs and models.DepDeployment.objects.filter(pk=self.kwargs['dep_id']):
            init['dep'] = models.DepDeployment.objects.get(pk=self.kwargs['dep_id'])

        if 'set_id' in self.kwargs and models.SetStationEventCode.objects.filter(pk=self.kwargs['set_id']):
            init['set_type'] = models.SetStationEventCode.objects.get(pk=self.kwargs['set_id'])
        return init


class StnCreate(mixins.StnMixin, CommonCreate):
    pass


class TeaCreate(mixins.TeaMixin, CommonCreate):
    pass


class CommonUpdate(CommonAuthUpdateView):

    nav_menu = 'whalesdb/base/whales_nav_menu.html'
    site_css = 'whalesdb/base/whales_css.css'
    home_url_name = "whalesdb:index"

    def get_success_url(self):
        success_url = self.success_url if self.success_url else reverse_lazy("whalesdb:list_{}".format(self.key))

        if self.kwargs.get("pop"):
            # create views intended to be pop out windows should close the window upon success
            success_url = reverse_lazy("shared_models:close_me_no_refresh")

        return success_url

    def get_nav_menu(self):
        if self.kwargs.get("pop"):
            return None

        return self.nav_menu

    # this function overrides UserPassesTestMixin.test_func() to determine if
    # the user should have access to this content, if the user is logged in
    # This function could be overridden in extending classes to preform further testing to see if
    # an object is editable
    def test_func(self):
        return self.request.user.groups.filter(name='whalesdb_admin').exists()

    # Get context returns elements used on the page. Make sure when extending to call
    # context = super().get_context_data(**kwargs) so that elements created in the parent
    # class are inherited by the extending class.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editable'] = context['auth']
        return context


class CruUpdate(mixins.CruMixin, CommonUpdate):

    def get_success_url(self):
        return reverse_lazy("whalesdb:details_cru", args=(self.kwargs['pk'],))


class DepUpdate(mixins.DepMixin, CommonUpdate):

     def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        station_dict = [{"stn_id": v[0], "stn_code": v[2]} for v in
                        models.StnStation.objects.all().order_by('pk').values_list()]

        context['station_json'] = json.dumps(station_dict)
        context['java_script'] = 'whalesdb/_entry_dep_js.html'

        context['editable'] = True
        if context['auth']:
            # editable if the object has no station events
            context['editable'] = self.model.objects.get(pk=self.kwargs['pk']).station_events.count() <= 0

        return context


class EcaUpdate(mixins.EcaMixin, CommonUpdate):
    def get_success_url(self):
        return reverse_lazy("whalesdb:details_eca", args=(self.kwargs['pk'],))


class EcpUpdate(mixins.EcpMixin, CommonUpdate):
    pass


class EmmUpdate(mixins.EmmMixin, CommonUpdate):

    def get_success_url(self):
        return reverse_lazy("whalesdb:list_emm")


class EqhUpdate(mixins.EqhMixin, CommonUpdate):
    pass


class EqpUpdate(mixins.EqpMixin, CommonUpdate):
    def get_success_url(self):
        return reverse_lazy("whalesdb:list_eqp")


class EqrUpdate(mixins.EqrMixin, CommonUpdate):
    pass


class EtrUpdate(mixins.EtrMixin, CommonUpdate):
    def get_success_url(self):
        return reverse_lazy("whalesdb:details_etr", args=(self.kwargs['pk'],))


class MorUpdate(mixins.MorMixin, CommonUpdate):

    def get_success_url(self):
        return reverse_lazy("whalesdb:list_mor")


class PrjUpdate(mixins.PrjMixin, CommonUpdate):
    def get_success_url(self):
        return reverse_lazy("whalesdb:list_prj")


class RecUpdate(mixins.RecMixin, CommonUpdate):

    def get_success_url(self):
        return reverse_lazy("whalesdb:details_rec", args=(self.kwargs['pk'],))


class ReeUpdate(mixins.ReeMixin, CommonUpdate):
    pass


class RetUpdate(mixins.RetMixin, CommonUpdate):

    def get_success_url(self):
        return reverse_lazy("whalesdb:list_ret")


class RscUpdate(mixins.RscMixin, CommonUpdate):

    def get_success_url(self):
        return reverse_lazy("whalesdb:list_rsc")


class StnUpdate(mixins.StnMixin, CommonUpdate):

    def get_success_url(self):
        return reverse_lazy("whalesdb:list_stn")


class SteUpdate(mixins.SteMixin, CommonUpdate):
    pass


class TeaUpdate(mixins.TeaMixin, CommonUpdate):
    def get_success_url(self):
        return reverse_lazy("whalesdb:list_tea")


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
    delete_url = None

    # By default detail objects are editable, set to false to remove update buttons
    editable = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.title:
            context['title'] = self.title

        if self.fields:
            context['fields'] = self.fields

        context['list_url'] = self.list_url if self.list_url else "whalesdb:list_{}".format(self.key)
        context['update_url'] = self.update_url if self.update_url else "whalesdb:update_{}".format(self.key)
        if self.delete_url:
            context['delete_url'] = self.delete_url

        # for the most part if the user is authorized then the content is editable
        # but extending classes can choose to make content not editable even if the user is authorized
        context['auth'] = utils.whales_authorized(self.request.user)
        context['editable'] = context['auth'] and self.editable

        return context


class CruDetails(mixins.CruMixin, CommonDetails):
    fields = ["institute", "mission_number", "mission_name", "description", "chief_scientist", "samplers", "start_date",
              "end_date", "probe", "area_of_operation", "number_of_profiles", "meds_id", "notes", "season","vessel", ]


class DepDetails(mixins.DepMixin, CommonDetails):
    template_name = 'whalesdb/details_dep.html'
    fields = ['dep_name', 'dep_year', 'dep_month', 'stn', 'prj', 'mor']

    delete_url = "whalesdb:delete_dep"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['google_api_key'] = settings.GOOGLE_API_KEY

        context['edit_attachments'] = self.model.objects.get(pk=self.kwargs['pk']).station_events.count()
        if models.EdaEquipmentAttachment.objects.filter(dep=self.kwargs['pk']):
            edas = models.EdaEquipmentAttachment.objects.filter(dep=self.kwargs['pk'])
            for eda in edas:
                if models.RecDataset.objects.filter(eda_id=eda.pk):
                    if not hasattr(context, 'rec'):
                        context['rec'] = []

                    rec = models.RecDataset.objects.filter(eda_id=eda.pk)
                    for r in rec:
                        context['rec'].append({
                            'text': str(r),
                            'id': r.pk,
                        })

        return context


class EcaDetails(mixins.EcaMixin, CommonDetails):
    template_name = 'whalesdb/details_eca.html'
    fields = ['eca_date', 'eca_attachment', 'eca_hydrophone', 'eca_notes']

    delete_url = 'whalesdb:delete_eca'


class EmmDetails(mixins.EmmMixin, CommonDetails):
    template_name = 'whalesdb/details_emm.html'
    fields = ['eqt', 'emm_make', 'emm_model', 'emm_depth_rating', 'emm_description']

    delete_url = "whalesdb:delete_emm"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class EtrDetails(mixins.EtrMixin, CommonDetails):
    fields = ['eqp', 'hyd', 'etr_date', 'etr_issue_desc', 'etr_repair_desc', 'etr_repaired_by', 'etr_dep_affe', 'etr_rec_affe']


class EqpDetails(mixins.EqpMixin, CommonDetails):
    template_name = "whalesdb/details_eqp.html"
    fields = ['emm', 'eqp_serial', 'eqp_asset_id', 'eqp_date_purchase', 'eqp_notes', 'eqp_retired', 'eqo_owned_by']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        channels = {}
        for hyd in self.object.hydrophones.all():
            channels[hyd.ecp_channel_no] = hyd

        context["channels"] = channels
        print(f"eqp auth: {context['auth']}")
        return context


class MorDetails(mixins.MorMixin, CommonDetails):
    template_name = 'whalesdb/details_mor.html'
    fields = ["mor_name", "mor_max_depth", "mor_link_setup_image", "mor_link_setup_pdf","mor_additional_equipment",
              "mor_general_moor_description", "mor_notes"]
    creation_form_height = 600


class PrjDetails(mixins.PrjMixin, CommonDetails):
    template_name = 'whalesdb/details_prj.html'
    fields = ['name', 'description_en', 'lead', 'prj_url']
    creation_form_height = 725


class RecDetails(mixins.RecMixin, CommonDetails):
    template_name = "whalesdb/details_rec.html"
    fields = ['eda_id', 'rsc_id', 'rtt_dataset', 'rtt_in_water', 'rec_start_date', 'rec_start_time', 'rec_end_date',
              'rec_end_time', 'rec_backup_hd_1', 'rec_backup_hd_2', 'rec_notes', ]

    delete_url = "whalesdb:delete_rec"


class RscDetails(mixins.RscMixin, CommonDetails):
    template_name = "whalesdb/details_rsc.html"
    fields = ['rsc_name', 'rsc_period']
    editable = False


class StnDetails(mixins.StnMixin, CommonDetails):
    template_name = 'whalesdb/details_stn.html'
    fields = ['stn_name', 'stn_code', 'stn_revision', 'stn_planned_lat', 'stn_planned_lon',
              'stn_planned_depth', 'stn_notes']
    creation_form_height = 400

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['google_api_key'] = settings.GOOGLE_API_KEY

        return context


class CommonList(CommonAuthFilterView):

    template_name = "whalesdb/whales_filter.html"
    nav_menu = 'whalesdb/base/whales_nav_menu.html'
    site_css = 'whalesdb/base/whales_css.css'
    home_url_name = "whalesdb:index"
    new_btn_text = "+"
    delete_confirm = True

    # fields to be used as columns to display an object in the filter view table
    fields = []

    field_list = [
        {"name": 'tname|{}'.format("name"), "class": "", "width": ""},
        {"name": 'tdescription|{}'.format("description"), "class": "", "width": ""},
    ]

    # URL to use to create a new object to be added to the filter view
    create_url = None

    # URL to use for the details button element in the filter view's list
    details_url = None

    # URL to use for the update button element in the filter view's list
    update_url = None

    # URL to use for the delete button element in the filter view's list
    delete_url = False

    # The height of the popup dialog used to display the creation/update form
    # if not set by the extending class the default popup height will be used
    creation_form_height = None

    # By default Listed objects will have an update button, set editable to false in extending classes to disable
    editable = True

    def get_h1(self):
        return self.get_title()
    
    def get_fields(self):
        if self.fields:
            return self.fields

        return ['tname|Name', 'tdescription|Description']

    def get_create_url(self):
        return self.create_url if self.create_url is not None else "whalesdb:create_{}".format(self.key)

    def get_details_url(self):
        return self.details_url if self.details_url is not None else "whalesdb:details_{}".format(self.key)

    def get_update_url(self):
        return self.update_url if self.update_url is not None else "whalesdb:update_{}".format(self.key)

    def get_delete_url(self):
        return self.delete_url if self.delete_url is not None else "whalesdb:delete_{}".format(self.key)

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, object_list=object_list, **kwargs)

        context['fields'] = self.get_fields()

        # if the url is not None, use the value specified by the url variable.
        # if the url is None, create a url using the views key
        # this way if no URL, say details_url, is provided it's assumed the default RUL will be 'whalesdb:details_key'
        # if the details_url = False in the extending view then False will be passed to the context['detials_url']
        # variable and in the template where the variable is used for buttons and links the button and/or links can
        # be left out without causing URL Not Found issues.
        context['create_url'] = self.get_create_url()
        context['new_object_url'] = reverse_lazy(context['create_url'])
        context['row_object_url_name'] = context['details_url'] = self.get_details_url()
        context['update_url'] = self.get_update_url()
        context['delete_url'] = self.get_delete_url()
        context['delete_confirm'] = self.delete_confirm
        # for the most part if the user is authorized then the content is editable
        # but extending classes can choose to make content not editable even if the user is authorized
        context['auth'] = utils.whales_authorized(self.request.user)
        context['editable'] = context['auth'] and self.editable

        if self.creation_form_height:
            context['height'] = self.creation_form_height

        return context


class CruList(mixins.CruMixin, CommonList):
    queryset = shared_models.Cruise.objects.all().order_by("-season", "mission_number")

    filterset_class = filters.CruFilter
    fields = ["mission_number", "description", "chief_scientist", "samplers", "start_date", "end_date", "notes",
              "season", "vessel" ]

    field_list = [
        {"name": "mission_number"},
        {"name": "description"},
        {"name": "chief_scientist"},
        {"name": "samplers"},
        {"name": "start_date"},
        {"name": "end_date"},
        {"name": "notes"},
        {"name": "season"},
        {"name": "vessel"},
    ]

    details_url = "whalesdb:details_cru"

    def test_func(self):
        return utils.whales_authorized(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class DepList(mixins.DepMixin, CommonList):
    filterset_class = filters.DepFilter
    fields = ['dep_name', 'dep_year', 'dep_month', 'stn', 'prj', 'mor']
    creation_form_height = 600

    field_list = [
        {"name": "dep_name"},
        {"name": "dep_year"},
        {"name": "dep_month"},
        {"name": "stn"},
        {"name": "prj"},
        {"name": "mor"},
    ]

    delete_url = "whalesdb:delete_dep"
    delete_confirm = False

    queryset = models.DepDeployment.objects.all().select_related("stn", "prj", "mor")

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, object_list=object_list, **kwargs)
        context['editable'] = False
        return context


class EcaList(mixins.EcaMixin, CommonList):
    filterset_class = filters.EcaFilter
    fields = ['eca_date', 'eca_attachment', 'eca_hydrophone']
    field_list = [
        {"name": "eca_date"},
        {"name": "eca_attachment"},
        {"name": "eca_hydrophone"},
    ]

    delete_url = 'whalesdb:delete_eca'
    delete_confirm = False


class EmmList(mixins.EmmMixin, CommonList):
    filterset_class = filters.EmmFilter
    fields = ['eqt', 'emm_make', 'emm_model', 'emm_depth_rating']
    field_list = [
        {"name": "eqt"},
        {"name": "emm_make"},
        {"name": "emm_model"},
        {"name": "emm_depth_rating"},
    ]

    delete_url = "whalesdb:delete_emm"
    delete_confirm = False


class EqpList(mixins.EqpMixin, CommonList):
    fields = ['emm', 'eqp_serial', 'eqp_date_purchase', 'eqo_owned_by', 'eqp_retired', "eqp_deployed"]
    field_list = [
        {"name": "emm"},
        {"name": "eqp_serial"},
        {"name": "eqp_date_purchase"},
        {"name": "eqo_owned_by"},
        {"name": "eqp_retired"},
        {"name": "eqp_deployed"},
    ]

    delete_url = "whalesdb:delete_eqp"
    delete_confirm = False


class EtrList(mixins.EtrMixin, CommonList):
    filterset_class = filters.EtrFilter
    fields = ['etr_date', 'eqp', 'etr_issue_desc', 'etr_repair_desc', 'etr_repaired_by', 'etr_dep_affe', 'etr_rec_affe']
    field_list = [
        {"name": "etr_date"},
        {"name": "eqp"},
        {"name": "hyd"},
        {"name": "etr_issue_desc"},
        {"name": "etr_repair_desc"},
        {"name": "etr_repaired_by"},
        {"name": "etr_dep_affe"},
        {"name": "etr_rec_affe"},
    ]

    delete_url = "whalesdb:delete_etr"
    delete_confirm = False


class MorList(mixins.MorMixin, CommonList):
    filterset_class = filters.MorFilter
    fields = ['mor_name', 'mor_max_depth', 'mor_notes']
    field_list = [
        {"name": "mor_name"},
        {"name": "mor_max_depth"},
        {"name": "mor_notes"},
    ]

    delete_url = "whalesdb:delete_mor"
    delete_confirm = False


class PrjList(mixins.PrjMixin, CommonList):
    filterset_class = filters.PrjFilter
    fields = ['tname|Name', 'tdescription|Description']

    delete_url = "whalesdb:delete_prj"
    delete_confirm = False


class RecList(mixins.RecMixin, CommonList):
    filterset_class = filters.RecFilter
    fields = ['eda_id', 'rsc_id', 'rec_start_date', 'rec_end_date']
    field_list = [
        {"name": "eda_id"},
        {"name": "rsc_id"},
        {"name": "rec_start_date"},
        {"name": "rec_end_date"},
    ]

    delete_url = "whalesdb:delete_rec"
    delete_confirm = False


class RetList(mixins.RetMixin, CommonList):
    filterset_class = filters.RetFilter
    fields = ['ret_name', 'ret_desc']
    field_list = [
        {"name": "ret_name"},
        {"name": "ret_desc"},
    ]

    details_url = False


class RscList(mixins.RscMixin, CommonList):
    filterset_class = filters.RscFilter
    fields = ['rsc_name', 'rsc_period']
    field_list = [
        {"name": "rsc_name"},
        {"name": "rsc_period"},
    ]

    delete_url = "whalesdb:delete_rsc"
    delete_confirm = False


class StnList(mixins.StnMixin, CommonList):
    filterset_class = filters.StnFilter
    fields = ['stn_name', 'stn_code', 'stn_revision']
    field_list = [
        {"name": "stn_name"},
        {"name": "stn_code"},
        {"name": "stn_revision"},
    ]

    delete_url = "whalesdb:delete_stn"
    delete_confirm = False


class TeaList(mixins.TeaMixin, CommonList):
    filterset_class = filters.TeaFilter
    fields = ["tea_abb", "tea_last_name", "tea_first_name"]
    field_list = [
        {"name": "tea_abb"},
        {"name": "tea_last_name"},
        {"name": "tea_first_name"},
    ]

    details_url = False
    delete_url = "whalesdb:delete_tea"
    delete_confirm = False


class CommonDeleteView(UserPassesTestMixin, CommonFormMixin, DeleteView):
    success_message = _('The Recording Schedule was successfully deleted!')
    template_name = 'whalesdb/confirm_delete.html'
    container_class = "container jumbotron curvy"

    # set this to false if you do not want the delete button to be greyed out if there are related objects
    delete_protection = True
    submit_text = None

    def get_h1(self):
        if self.h1:
            return self.h1
        else:
            return gettext(
                "Are you sure you want to delete the following {}? <br>  <span class='red-font h4'>{}</span>".format(
                    self.model._meta.verbose_name,
                    self.get_object(),
                ))

    def get_cancel_url(self):
        if 'pop' in self.kwargs:
            return reverse_lazy('shared_models:close_me_no_refresh')

        return super().get_cancel_url()

    def get_submit_text(self):
        if self.submit_text:
            return self.submit_text
        else:
            return gettext("Delete")

    def get_related_names(self):
        """if a related_names list was provided, this will turn the simple list into a more complex list that is ready for template digestion"""
        my_list = list()
        field_map_dict = type(self.get_object())._meta.fields_map
        for field in field_map_dict:
            # some of these might be M2M fields...
            temp_related_name = field_map_dict[field].related_name

            if not temp_related_name:
                related_name = f"{field}_set"
            elif "+" not in temp_related_name:
                related_name = field_map_dict[field].related_name
            else:
                related_name = None

            if related_name:
                try:
                    my_list.append(
                        {
                            "title": getattr(type(self.get_object()),
                                             related_name).rel.related_model._meta.verbose_name_plural,
                            "qs": getattr(self.get_object(), related_name).all()
                        }
                    )
                except AttributeError:
                    pass
        return my_list

    def test_func(self):
        return utils.whales_authorized(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)

    def get_delete_protection(self):
        if not self.delete_protection:
            return False
        else:
            # the user wants delete protection to be turned on

            # go through each related field. If there is a related object, we set set a flag and exit the loop
            field_map_dict = type(self.get_object())._meta.fields_map
            for field in field_map_dict:
                temp_related_name = field_map_dict[field].related_name

                if not temp_related_name:
                    related_name = f"{field}_set"
                elif "+" not in temp_related_name:
                    related_name = field_map_dict[field].related_name
                else:
                    related_name = None

                # the second we find a related object, we are done here.
                try:
                    getattr(self.get_object(), related_name)
                except:
                    pass
                else:
                    attr = getattr(self.get_object(), related_name)
                    attr_type = getattr(type(self.get_object()), related_name)
                    if not isinstance(attr_type, ReverseOneToOneDescriptor) and related_name and attr.count():
                        return True
            # if we got to this point, delete protection should be set to false, since there are no related objects
            return False

    def get_success_url(self):
        if 'pop' in self.kwargs:
            return reverse_lazy('shared_models:close_me')

        return reverse_lazy(f'whalesdb:list_{self.key}')

    def get_active_page_name_crumb(self):
        if self.active_page_name_crumb:
            return self.active_page_name_crumb
        else:
            return gettext("Delete Confirmation")

    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        context.update(super().get_common_context())
        context["model_name"] = self.get_object()._meta.verbose_name
        context["related_names"] = self.get_related_names()
        context["delete_protection"] = self.get_delete_protection()
        if 'pop' in self.kwargs:
            context['show_nav'] = False

        return context


class DepDeleteView(mixins.DepMixin, CommonDeleteView):
    pass


class EcaDeleteView(mixins.EcaMixin, CommonDeleteView):
    pass


class EccDeleteView(mixins.EccMixin, CommonDeleteView):
    pass


class EcpDeleteView(mixins.EcpMixin, CommonDeleteView):
    pass


class EdaDeleteView(mixins.EdaMixin, CommonDeleteView):
    pass


class EmmDeleteView(mixins.EmmMixin, CommonDeleteView):

    def delete(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        emm = models.EmmMakeModel.objects.get(pk=pk)
        if emm.eqt.pk == 4 and models.EqhHydrophoneProperty.objects.filter(emm=emm).count() > 0:
            eqh = models.EqhHydrophoneProperty.objects.get(emm=emm)
            eqh.delete()
        elif models.EqrRecorderProperties.objects.filter(emm=emm).count() > 0:
            eqr = models.EqrRecorderProperties.objects.get(emm=emm)
            eqr.delete()

        return super().delete(request, *args, **kwargs)


class EqpDeleteView(mixins.EqpMixin, CommonDeleteView):
    pass


class EtrDeleteView(mixins.EtrMixin, CommonDeleteView):
    pass


class MorDeleteView(mixins.MorMixin, CommonDeleteView):
    pass


class PrjDeleteView(mixins.PrjMixin, CommonDeleteView):
    pass


class RciDeleteView(mixins.RciMixin, CommonDeleteView):
    pass


class RecDeleteView(mixins.RecMixin, CommonDeleteView):
    pass


class ReeDeleteView(mixins.ReeMixin, CommonDeleteView):
    pass


class RscDeleteView(mixins.RscMixin, CommonDeleteView):
    pass


class RstDeleteView(mixins.RstMixin, CommonDeleteView):
    pass


class SteDeleteView(mixins.SteMixin, CommonDeleteView):
    pass


class StnDeleteView(mixins.StnMixin, CommonDeleteView):
    pass


def delete_managed(request, key, pk):
    if utils.whales_authorized(request.user):

        if key == 'eqt':
            models.EqtEquipmentTypeCode.objects.get(pk=pk).delete()
            messages.success(request, _("The recording stage has been successfully deleted."))
        elif key == 'rtt':
            models.EqtEquipmentTypeCode.objects.get(pk=pk).delete()
            messages.success(request, _("The recording stage has been successfully deleted."))

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse_lazy('accounts:denied_access'))


class ManagedFormsetViewMixin(AdminRequiredMixin, CommonFormsetView):
    template_name = 'whalesdb/managed_formset.html'
    home_url_name = "whalesdb:index"
    delete_url_name = "whalesdb:delete_managed"
    container_class = "container bg-light curvy"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['key'] = self.key

        return context


class EheMangedView(ManagedFormsetViewMixin):
    key = 'ehe'
    h1 = "Manage Equipment Channel History"
    queryset = models.EheHydrophoneEvent.objects.all()
    formset_class = forms.EheFormset
    success_url = reverse_lazy("whalesdb:managed_ehe")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.kwargs and self.kwargs['rec']:
            qs = qs.filter(rec=self.kwargs['rec'])

        if self.kwargs and self.kwargs['ecp_channel_no']:
            qs = qs.filter(ecp_channel_no=self.kwargs['ecp_channel_no'])

        return qs

    def get_success_url(self):
        return reverse_lazy("whalesdb:managed_ehe", kwargs=self.kwargs)

    def get_cancel_url(self):
        if self.kwargs and self.kwargs['rec']:
            return reverse_lazy("whalesdb:details_eqp", args=[self.kwargs['rec']])

        return reverse_lazy("whalesdb:list_eqp")


class EqtMangedView(ManagedFormsetViewMixin):
    key = 'eqt'
    h1 = "Manage Equipment Type"
    queryset = models.EqtEquipmentTypeCode.objects.all()
    formset_class = forms.EqtFormset
    success_url = reverse_lazy("whalesdb:managed_eqt")


class ErtMangedView(ManagedFormsetViewMixin):
    key = 'ert'
    h1 = "Manage Recorder Type"
    queryset = models.ErtRecorderType.objects.all()
    formset_class = forms.ErtFormset
    success_url = reverse_lazy("whalesdb:managed_ert")


class PrmMangedView(ManagedFormsetViewMixin):
    key = 'prm'
    h1 = "Manage Parameter codes"
    queryset = models.PrmParameterCode.objects.all()
    formset_class = forms.PrmFormset
    success_url = reverse_lazy("whalesdb:managed_prm")


class RttMangedView(ManagedFormsetViewMixin):
    key = 'rtt'
    h1 = "Manage Timezone codes"
    queryset = models.RttTimezoneCode.objects.all()
    formset_class = forms.RttFormset
    success_url = reverse_lazy("whalesdb:managed_rtt")


class SetMangedView(ManagedFormsetViewMixin):
    key = 'set'
    h1 = "Manage Station Event codes"
    queryset = models.SetStationEventCode.objects.all()
    formset_class = forms.SetFormset
    success_url = reverse_lazy("whalesdb:managed_set")


class HelpTextFormsetView(UserPassesTestMixin, CommonFormsetView):
    template_name = 'whalesdb/formset.html'
    title = _("Whales Help Text")
    h1 = _("Manage Help Texts")
    queryset = models.HelpText.objects.all()
    formset_class = forms.HelpTextFormset
    success_url_name = "whalesdb:manage_help_texts"
    home_url_name = "whalesdb:index"
    delete_url_name = "whalesdb:delete_help_text"

    def test_func(self):
        return utils.whales_authorized(self.request.user)


class HelpTextHardDeleteView(UserPassesTestMixin, CommonHardDeleteView):
    model = models.HelpText
    success_url = reverse_lazy("whalesdb:manage_help_texts")

    def test_func(self):
        return utils.whales_authorized(self.request.user)
