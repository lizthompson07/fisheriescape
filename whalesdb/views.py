from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django_filters.views import FilterView
from django.utils.translation import gettext_lazy as _

import json
import datetime

from . import forms
from . import models
from . import filters


def get_id(model, sort):
    obj = model.objects.all().order_by('-' + sort).values_list()

    n_id = 1
    if obj and obj[0][0]:
        n_id = int(obj[0][0]) + 1

    return n_id


# Parameter deletion
def par_delete(request, url, emm_id, prm_id):
    try:
        emm = models.EmmMakeModel.objects.get(emm_id=emm_id)
        prm = models.PrmParameterCode.objects.get(prm_id=prm_id)

        prm_obj = models.EprEquipmentParameters.objects.get(emm=emm, prm=prm)

        prm_obj.delete()

    finally:
        return HttpResponseRedirect(reverse("whalesdb:details_"+url, kwargs={'pk': emm_id}))


# Channel Deletion
def ecp_delete(request, ecp_id):
    try:
        ecp = models.EcpChannelProperties.objects.get(ecp_id=ecp_id)
        emm_id = ecp.emm.emm_id
        ecp.delete()
    finally:
        return HttpResponseRedirect(reverse("whalesdb:details_eqr", kwargs={'pk': emm_id}))


def get_fields(labels):
    fields = []
    for key in labels.keys():
        fields.append({
            'label': labels[key],
            'key': key
        })

    return fields


def get_model_object(obj_name):
    obj_def = {}

    ''' 
    The object definition tells the CodeEditView, or similar class, how to process a code list object.
    It also tells the code_list.html, or similar list view, how to display the codelist
    
    obj_def = {
        'label': "ADC-Bits",            <- Label used as the title of the code entry dialog and list heading
        'url': obj_name,                <- Object name, same name used in the URL for the code entry and list
        'order': "eqa_id",              <- The column query results are sorted by
        'model': models.EqaAdcBitsCode, <- The model to use when creating a DB column row
        'entry': "code_entry",          <- Default should be code_entry, but specify if a different url.py name is used
        'fields': [_("ID"), _("Value")] <- Fields to display on the code list page
    }
    '''

    if obj_name == 'eqa':
        obj_def = {
            'label': "ADC-Bits",
            'url': obj_name,
            'order': "eqa_id",
            'model': models.EqaAdcBitsCode,
            'entry': obj_name,
            'fields': [_("ID"), _("Value")]
        }
    elif obj_name == 'eqt':
        obj_def = {
            'label': "Equipment Type",
            'url': obj_name,
            'order': "eqt_id",
            'model': models.EqtEquipmentTypeCode,
            'entry': obj_name,
            'fields': [_("ID"), _("Value")]
        }
    elif obj_name == 'prm':
        obj_def = {
            'label': "Equipment Parameter",
            'url': obj_name,
            'order': "prm_id",
            'model': models.PrmParameterCode,
            'entry': obj_name,
            'fields': [_("ID"), _("Value")]
        }
    elif obj_name == 'set':
        obj_def = {
            'label': "Station Event",
            'url': obj_name,
            'order': "set_id",
            'model': models.SetStationEventCode,
            'entry': obj_name,
            'fields': [_("ID"), _("Name"), _("Description")]
        }
    elif obj_name == 'tea':
        obj_def = {
            'label': "Team Member",
            'url': obj_name,
            'order': "tea_last_name",
            'model': models.TeaTeamMembers,
            'entry': obj_name,
            'fields': [_("ID"), _("Abbv."), _("Last Name"), _("First Name")]
        }
    elif obj_name == 'rtt':
        obj_def = {
            'label': "Time Zone",
            'url': obj_name,
            'order': "rtt_offset",
            'model': models.RttTimezoneCode,
            'entry': obj_name,
            'fields': [_("ID"), _("Abbreviation"), _("Name"), _("Offset from GMT")]
        }

    return obj_def


def get_smart_object(obj_name):
    obj_def = {}

    ''' 
    The smart object definition tells the CreateSmartForm, UpdateSmartForm and List smart classes how to process a 
    model object.

    obj_def = {
        'model': models.StnStations, <-- The model represented by the obj_name
        'form_class': forms.StationForm, <-- The form to use when the 'Crete New' button is checked on the list page

        'filter_class': filters.StnFilter, <-- the filter class to use on the list page
        'title': "Stations", <-- the human readable title to use on the list page
    }
    '''

    if obj_name == 'crs':
        obj_def = {
            'model': models.CrsCruises,
            'form_class': forms.CrsForm,

            'filter_class': filters.CrsFilter,
            'title': "Cruises",
        }
    elif obj_name == 'dep':
        obj_def = {
            'model': models.DepDeployments,
            'form_class': forms.DepForm,

            'filter_class': filters.DepFilter,
            'title': "Deployments",
        }
    elif obj_name == 'eda':
        obj_def = {
            'model': models.EdaEquipmentAttachments,
            'form_class': forms.EdaForm,

            'filter_class': filters.EdaFilter,
            'title': "Equipment Attachements",
        }
    elif obj_name == 'edh':
        obj_def = {
            'model': models.EhaHydrophoneAttachements,
            'form_class': forms.EdhForm,

            'filter_class': filters.EdhFilter,
            'title': "Hydrophone Attachements",
        }
    elif obj_name == 'eqh':
        obj_def = {
            'model': models.EqhHydrophoneProperties,
            'filterset_class': filters.EqhFilter,

            'create_link': 'whalesdb:create_eqh',
            'detail_link': 'whalesdb:details_eqh',
            'title': 'Hydrophone Equipment',
        }
    elif obj_name == 'eqp':
        obj_def = {
            'model': models.EqpEquipment,
            'form_class': forms.EqpForm,

            'filter_class': filters.EqpFilter,
            'title': "Equipment",
        }
    elif obj_name == 'mor':
        obj_def = {
            'model': models.MorMooringSetups,
            'form_class': forms.MorForm,

            'filter_class': filters.MorFilter,
            'title': "Mooring Setups",
        }
    elif obj_name == 'prj':
        obj_def = {
            'model': models.PrjProjects,
            'form_class': forms.PrjForm,

            'filter_class': filters.PrjFilter,
            'title': "Projects",
        }
    elif obj_name == 'rec':
        obj_def = {
            'model': models.RecRecordingEvents,
            'form_class': forms.RecForm,

            'filter_class': filters.RecFilter,
            'title': "Recording Events",
        }
    elif obj_name == 'rsc':
        obj_def = {
            'model': models.RscRecordingSchedules,
            'form_class': forms.RscForm,

            'filter_class': filters.RscFilter,
            'title': "Recording Schedules",
        }
    elif obj_name == 'rst':
        obj_def = {
            'model': models.RstRecordingStage,
            'form_class': forms.RstForm,

            'filter_class': filters.RstFilter,
            'title': "Recording Stages",
        }
    elif obj_name == 'ste':
        obj_def = {
            'model': models.SteStationEvents,
            'form_class': forms.SteForm,

            'filter_class': filters.SteFilter,
            'title': "Station Events",
        }
    elif obj_name == 'stn':
        obj_def = {
            'model': models.StnStations,
            'form_class': forms.StnForm,

            'filter_class': filters.StnFilter,
            'title': "Stations",
        }

    else:
        raise Exception("No get_smart_object named '" + obj_name + "'")

    obj_def['obj_name'] = obj_name

    return obj_def


class IndexView(TemplateView):
    template_name = 'whalesdb/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['section'] = [
            {
                'title': 'Deployment',
                'forms': [
                    {
                        'obj_name': 'stn',
                        'title': "Stations",
                        'url': "whalesdb:list_obj",
                        'icon': "img/whales/station.svg",
                    },
                    {
                        'obj_name': 'prj',
                        'title': "Project",
                        'url': "whalesdb:list_obj",
                        'icon': "img/whales/project.svg",
                    },
                    {
                        'obj_name': 'mor',
                        'title': "Mooring Setup",
                        'url': "whalesdb:list_obj",
                        'icon': "img/whales/mooring.svg",
                    },
                    {
                        'obj_name': 'crs',
                        'title': "Cruise",
                        'url': "whalesdb:list_obj",
                        'icon': 'img/icons/boat.svg',
                    },
                    {
                        'obj_name': 'dep',
                        'title': "Deployment",
                        'url': "whalesdb:list_obj",
                        'icon': "img/whales/deployment.svg",
                    },
                    {
                        'obj_name': 'ste',
                        'title': "Station Event",
                        'url': "whalesdb:list_obj",
                        'icon': 'img/icons/boat.svg',
                    },
                ],
                'code': [
                    {
                        'type': 'codelist',
                        'title': "Station Event Code Table",
                        'url': "set",
                        'icon': "img/whales/station.svg",
                    },
                ]
            },
            {
                'title': 'Recording',
                'forms': [
                    {
                        'obj_name': 'rec',
                        'title': "Recording Event",
                        'url': "whalesdb:list_obj",
                        'icon': "img/whales/record.svg"
                    },
                    {
                        'obj_name': 'rsc',
                        'title': "Recording Schedules",
                        'url': "whalesdb:list_obj",
                        'icon': "img/whales/record_schedule.svg"
                    },
                    {
                        'obj_name': 'rst',
                        'title': "Recording Stage",
                        'url': "whalesdb:list_obj",
                        'icon': "img/whales/record_stage.svg"
                    },
                ],
                'code': [
                    {
                        'type': 'codelist',
                        'title': "Team Member",
                        'url': "tea",
                        'icon': "img/whales/team.svg"
                    },
                    {
                        'type': 'codelist',
                        'title': 'Time Zone',
                        'url': 'rtt',
                        'icon': "img/whales/clock.svg"
                    }
                ]
            },
            {
                'title': 'Equipment Inventory',
                'forms': [
                    {
                        'title': "Hydrophone",
                        'url': "whalesdb:list_eqh",
                        'icon': "img/whales/microphone.svg",
                    },
                    {
                        'title': "Recorder",
                        'url': "whalesdb:list_eqr",
                        'icon': "img/whales/record.svg",
                    },
                    {
                        'obj_name': "eqp",
                        'title': "Equipment",
                        'url': "whalesdb:list_obj",
                        'icon': "img/whales/equipment.svg",
                    },
                    {
                        'obj_name': "eda",
                        'title': "Equipment Attachments",
                        'url': "whalesdb:list_obj",
                        'icon': "img/whales/record_attach.svg",
                    },
                    {
                        'obj_name': "edh",
                        'title': "Hydrophone Attachments",
                        'url': "whalesdb:list_obj",
                        'icon': "img/whales/microphone_attach.svg",
                    },
                ],
                'code': [
                    {
                        'type': 'codelist',
                        'title': "ADC Bits Code Table",
                        'url': "eqa",
                        'icon': "img/whales/transfer.svg",
                    },
                    {
                        'type': 'codelist',
                        'title': "Parameter Code Table",
                        'url': "prm",
                        'icon': "img/whales/function.svg",
                    },
                    {
                        'type': 'codelist',
                        'title': "Equipment Type Code Table",
                        'url': "eqt",
                        'icon': "img/whales/equipment_type.svg",
                    },
                ]
            },
        ]

        return context


class CloserTemplateView(TemplateView):
    template_name = 'whalesdb/close_me.html'


class CloserNoRefreshTemplateView(TemplateView):
    template_name = 'whalesdb/close_me_no_refresh.html'


class UpdateTemplate(UpdateView):
    template_name = "whalesdb/create_default.html"
    success_url = "#"
    cancel_url = "whalesdb:index"

    def get_initial(self):
        if 'pop' in self.kwargs and self.kwargs['pop']=='pop':
            self.template_name = "whalesdb/create_default_no_head.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.cancel_url

        if hasattr(self, 'obj_name'):
            context['obj_name'] = self.obj_name

        if 'pop' in self.kwargs and self.kwargs['pop']=='pop':
            context["pop"] = True

        return context


class CreateTemplate(CreateView):
    template_name = "whalesdb/create_default.html"
    success_url = "#"
    cancel_url = "whalesdb:index"

    def get_initial(self):
        if 'pop' in self.kwargs and self.kwargs['pop']=='pop':
            self.template_name = "whalesdb/create_default_no_head.html"
            self.success_url = reverse_lazy("whalesdb:close_me")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.cancel_url

        if hasattr(self, 'obj_name'):
            context['obj_name'] = self.obj_name

        if 'pop' in self.kwargs and self.kwargs['pop']=='pop':
            context["pop"] = True

        return context


class CreateSmartForm(LoginRequiredMixin, CreateTemplate):

    login_url = '/accounts/login_required/'

    def setup(self, request, *args, **kwargs):
        obj_def = get_smart_object(kwargs['obj_name'])

        self.model = obj_def['model']
        self.form_class = obj_def['form_class']
        self.success_url = reverse_lazy('whalesdb:list_obj', kwargs={'obj_name': kwargs['obj_name']})
        self.cancel_url = obj_def['url'] if 'url' in obj_def else 'whalesdb:list_obj'
        self.obj_name = kwargs['obj_name']

        super().setup(request, *args, **kwargs)


class UpdateSmartForm(LoginRequiredMixin, UpdateTemplate):

    login_url = '/accounts/login_required/'

    def setup(self, request, *args, **kwargs):

        obj_def = get_smart_object(kwargs['obj_name'])

        self.model = obj_def['model']
        self.form_class = obj_def['form_class']
        self.success_url = reverse_lazy('whalesdb:list_obj', kwargs={'obj_name': kwargs['obj_name']})
        self.cancel_url = obj_def['url'] if 'url' in obj_def else 'whalesdb:list_obj'
        self.obj_name = kwargs['obj_name']

        super().setup(request, *args, **kwargs)


class CreatePrmParameter(CreateTemplate):
    form_class = forms.EprForm

    def form_valid(self, form):
        form.save(commit=False)

        emm_id = self.kwargs['emm_id']
        emm = models.EmmMakeModel.objects.get(pk=emm_id)

        epr = models.EprEquipmentParameters(emm=emm, prm=form.cleaned_data['prm'])

        epr.save()

        return HttpResponseRedirect(reverse("whalesdb:close_me"))


class CreateChannel(CreateTemplate):
    form_class = forms.EcpChannelPropertiesForm

    def form_valid(self, form):
        form.save(commit=False)

        emm_id = self.kwargs['emm_id']
        emm = models.EmmMakeModel.objects.get(pk=emm_id)

        ecp = models.EcpChannelProperties(emm=emm, ecp_channel_no=form.cleaned_data['ecp_channel_no'],
                                          eqa_adc_bits=form.cleaned_data['eqa_adc_bits'],
                                          ecp_voltage_range_min=form.cleaned_data['ecp_voltage_range_min'],
                                          ecp_voltage_range_max=form.cleaned_data['ecp_voltage_range_max'],
                                          ecp_gain=form.cleaned_data['ecp_gain'])

        ecp.save()

        return HttpResponseRedirect(reverse("whalesdb:close_me"))


class CreateEMM(CreateChannel):

    def form_valid(self, form):
        form.save(commit=False)

        emm = models.EmmMakeModel(eqt=models.EqtEquipmentTypeCode.objects.get(pk=form.cleaned_data['eqt']),
                                  emm_make=form.cleaned_data['emm_make'],
                                  emm_model=form.cleaned_data['emm_model'],
                                  emm_depth_rating=form.cleaned_data['emm_depth_rating'],
                                  emm_description=form.cleaned_data['emm_description'])

        emm.save(force_insert=True)

        ''' for some reason I cannot use the emm object I just created. Trying to use it to create the
            hydrophone properties object will result in a "ValueObject" error. I assume that's because
            the emm.emm_id isn't set until the object has been inserted into the database, even after the insert
            this *object* doesn't have the emm.emm_id.

            To compensate I query the DB and get the most recently inserted emm object '''

        return models.EmmMakeModel.objects.all().order_by("-pk")[0]


class CreateRecorder(CreateEMM):
    form_class = forms.EmmForm
    success_url = "whalesdb:list_eqr"
    cancel_url = success_url


class CreateHydrophone(CreateEMM):
    form_class = forms.EqhForm
    success_url = "whalesdb:list_eqh"
    cancel_url = success_url

    def form_valid(self, form):
        emm = super().form_valid(form)

        eqh = models.EqhHydrophoneProperties(emm=emm,
                                             eqh_range_min=form.cleaned_data['eqh_range_min'],
                                             eqh_range_max=form.cleaned_data['eqh_range_max'])
        eqh.save()

        return HttpResponseRedirect(reverse('whalesdb:details_eqh', kwargs={'pk': eqh.pk}))


class CreateDeployment(LoginRequiredMixin, CreateTemplate):
    model = models.DepDeployments
    template_name = "whalesdb/create_deployment.html"
    success_url = "#"
    cancel_url = "whalesdb:index"
    form_class = forms.DepForm

    def get_initial(self):
        initial = super().get_initial()

        if initial:
            initial = initial.copy()
        else:
            initial = {}

        now = datetime.datetime.now()

        initial['dep_year'] = now.year
        initial['dep_month'] = now.month

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        station_dict = [{"stn_id": v[0], "stn_code": v[2]} for v in models.StnStations.objects.all().order_by('stn_id').values_list()]

        context['station_json'] = json.dumps(station_dict)
        return context


class UpdateDeployment(LoginRequiredMixin, UpdateTemplate):
    model = models.DepDeployments
    template_name = "whalesdb/create_deployment.html"
    success_url = "#"
    cancel_url = "whalesdb:index"
    form_class = forms.DepForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        station_dict = [{"stn_id": v[0], "stn_code": v[2]} for v in models.StnStations.objects.all().order_by('stn_id').values_list()]

        context['station_json'] = json.dumps(station_dict)
        return context


class DetailsMakeModel(DetailView):
    template_name = "whalesdb/details_make_model.html"

    def get_emm(self):
        return models.EmmMakeModel.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['objects'] = []

        if hasattr(kwargs['object'], 'emm'):
            labels = forms.get_descriptions(models.EmmMakeModel)
            context['objects'].append({
                "object": kwargs['object'].emm,
                "fields": get_fields(labels)
            })

            labels = forms.get_short_labels(models.EprEquipmentParameters)
            context['parameter_fields'] = get_fields(labels)
            context['parameter'] = [p for p in models.EprEquipmentParameters.objects.filter(emm=self.get_emm())]

        return context


class DetailsRecorder(DetailsMakeModel):
    model = models.EmmMakeModel

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        labels = forms.get_descriptions(models.EmmMakeModel)
        context['objects'].append({
            "object": kwargs['object'],
            "fields": get_fields(labels)
        })

        labels = forms.get_short_labels(models.EcpChannelProperties)
        context['channel_fields'] = get_fields(labels)
        context['channels'] = [c for c in models.EcpChannelProperties.objects.filter(emm=kwargs['object'])]
        context['url'] = 'eqr'

        labels = forms.get_short_labels(models.EprEquipmentParameters)
        context['parameter_fields'] = get_fields(labels)
        context['parameter'] = [p for p in models.EprEquipmentParameters.objects.filter(emm=kwargs['object'])]

        return context


class DetailsHydrophone(DetailsMakeModel):
    model = models.EqhHydrophoneProperties

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        labels = forms.get_descriptions(models.EqhHydrophoneProperties)
        context['objects'].append({
            "object": kwargs['object'],
            "fields": get_fields(labels)
        })
        context['url'] = 'eqh'

        return context


class ListGeneric(FilterView):
    template_name = 'whalesdb/filter_inventory.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        labels = forms.get_short_labels(self.model)
        context['fields'] = get_fields(labels)
        context['new_object'] = self.create_link
        context['detail_object'] = self.detail_link if hasattr(self, 'detail_link') else self.create_link
        context["detail_type"] = self.detail_type if hasattr(self, 'detail_type') else 'general'
        context["title"] = self.title

        if hasattr(self, 'obj_name'):
            context['obj_name'] = self.obj_name

        return context


class ListEMM(ListGeneric):
    detail_type = 'emm'


class ListRecorder(ListEMM):
    model = models.EmmMakeModel
    filterset_class = filters.EmmFilter
    detail_type = 'general'
    create_link = "whalesdb:create_eqr"
    detail_link = "whalesdb:details_eqr"
    title = "Recorder Equipment"


class ListHydrophone(ListEMM):
    model = models.EqhHydrophoneProperties
    filterset_class = filters.EqhFilter
    create_link = "whalesdb:create_eqh"
    detail_link = "whalesdb:details_eqh"
    title = "Hydrophone Equipment"


class ListSmart(ListGeneric):

    def setup(self, request, *args, **kwargs):
        obj_def = get_smart_object(kwargs['obj_name'])
        self.model = obj_def['model']
        self.filterset_class = obj_def['filter_class']
        self.create_link = obj_def['create_link'] if 'create_link' in obj_def else 'whalesdb:create_obj'
        self.title = obj_def['title']

        if 'obj_name' in obj_def:
            self.obj_name = obj_def['obj_name']

        return super().setup(request, *args, **kwargs)


class CodeListView(ListView):
    template_name = "whalesdb/code_list.html"
    model = models.EqaAdcBitsCode

    def get_queryset(self):
        obj_def = get_model_object(self.kwargs['lookup'])
        qs = obj_def['model'].objects.all().order_by(obj_def['order']).values_list()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['lookup'] = get_model_object(self.kwargs['lookup'])
        return context


class SimpleEditView(LoginRequiredMixin, CreateView):
    login_url = '/accounts/login_required/'
    template_name = "whalesdb/code_entry.html"

    success_url = reverse_lazy('whalesdb:close_me')

    def get_initial(self):
        return super().get_initial()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj_def = get_model_object(self.view_code)

        context["title"] = obj_def["label"]
        return context


class PrmCodeEditView(SimpleEditView):

    form_class = forms.PrmForm
    view_code = "prm"

    def get_initial(self):
        initial = super().get_initial()

        initial['prm_id'] = get_id(models.PrmParameterCode, 'prm_id')

        return initial


class EqaCodeEditView(SimpleEditView):

    form_class = forms.EqaForm
    view_code = "eqa"

    def get_initial(self):
        initial = super().get_initial()

        initial['eqa_id'] = get_id(models.EqaAdcBitsCode, 'eqa_id')

        return initial


class EqtCodeEditView(SimpleEditView):

    form_class = forms.EqtForm
    view_code = "eqt"

    def get_initial(self):
        initial = super().get_initial()

        initial['eqt_id'] = get_id(models.EqtEquipmentTypeCode, 'eqt_id')

        return initial


class RttCodeEditView(SimpleEditView):
    form_class = forms.RttForm
    view_code = "rtt"

    def get_initial(self):
        initial = super().get_initial()

        initial['rtt_id'] = get_id(models.RttTimezoneCode, 'rtt_id')

        return initial


class SetCodeEditView(SimpleEditView):

    form_class = forms.SetForm
    view_code = "set"

    def get_initial(self):
        initial = super().get_initial()

        initial['set_id'] = get_id(models.SetStationEventCode, 'set_id')

        return initial


class TeaCodeEditView(SimpleEditView):
    form_class = forms.TeaForm
    view_code = "tea"
