from django.views.generic import TemplateView, CreateView, ListView, DetailView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django_filters.views import FilterView
from django.utils.translation import gettext_lazy as _

import re

from . import forms
from . import models
from . import filters


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

    if obj_name == 'adcbits':
        obj_def = {
            'label': "ADC-Bits",
            'url': obj_name,
            'order': "eqa_id",
            'model': models.EqaAdcBitsCode,
            'entry': "code_entry",
            'fields': [_("ID"), _("Value")]
        }
    elif obj_name == 'parameter':
        obj_def = {
            'label': "Equipment Parameter",
            'url': obj_name,
            'order': "prm_id",
            'model': models.PrmParameterCode,
            'entry': "code_entry",
            'fields': [_("ID"), _("Value")]
        }
    elif obj_name == 'equipment_type':
        obj_def = {
            'label': "Equipment Type",
            'url': obj_name,
            'order': "eqt_id",
            'model': models.EqtEquipmentTypeCode,
            'entry': "code_entry",
            'fields': [_("ID"), _("Value")]
        }
    elif obj_name == 'station_event':
        obj_def = {
            'label': "Station Event",
            'url': obj_name,
            'order': "set_id",
            'model': models.SetStationEventCode,
            'entry': obj_name,
            'fields': [_("ID"), _("Name"), _("Description")]
        }

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
                        'title': "Create Cruise",
                        'url': "whalesdb:create_crs",
                        'icon': 'img/icons/boat.svg',
                    },
                    {
                        'title': "Create Station",
                        'url': "whalesdb:create_stn",
                        'icon': "img/whales/station.svg",
                    },
                    {
                        'title': "Create Project",
                        'url': "whalesdb:create_prj",
                        'icon': "img/whales/project.svg",
                    },
                    {
                        'title': "Create Mooring Setup",
                        'url': "whalesdb:create_mor",
                        'icon': "img/whales/equipment.svg",
                    },
                    {
                        'title': "Create Deployment",
                        'url': "whalesdb:create_dep",
                        'icon': "img/whales/deployment.svg",
                    },
                    {
                        'title': "Create Station Event",
                        'url': "whalesdb:create_ste",
                        'icon': 'img/icons/boat.svg',
                    },
                ],
                'code': [
                    {
                        'type': 'codelist',
                        'title': "Station Event Code Table",
                        'url': "station_event",
                        'icon': "img/whales/station.svg",
                    },
                ]
            },
            {
                'title': 'Recording',
                'forms': [
                    {
                        'title': "Recording Event",
                        'url': "whalesdb:list_rec",
                        'icon': "img/whales/record.svg"
                    },
                    {
                        'title': "Recording Schedules",
                        'url': "whalesdb:create_rsc",
                        'icon': "img/whales/record_schedule.svg"
                    },
                    {
                        'title': "Recording Stage",
                        'url': "whalesdb:create_rst",
                        'icon': "img/whales/record_stage.svg"
                    },
                    {
                        'title': "Team Member",
                        'url': "whalesdb:create_tea",
                        'icon': "img/whales/team.svg"
                    }

                ]
            },
            {
                'title': 'Equipment Inventory',
                'forms': [
                    {
                        'title': "Hydrophone",
                        'url': "whalesdb:list_hydrophone",
                        'icon': "img/whales/microphone.svg",
                    },
                    {
                        'title': "Recorder",
                        'url': "whalesdb:list_recorder",
                        'icon': "img/whales/record.svg",
                    },
                ],
                'code': [
                    {
                        'type': 'codelist',
                        'title': "ADC Bits Code Table",
                        'url': "adcbits",
                        'icon': "img/whales/transfer.svg",
                    },
                    {
                        'type': 'codelist',
                        'title': "Parameter Code Table",
                        'url': "parameter",
                        'icon': "img/whales/function.svg",
                    },
                    {
                        'type': 'codelist',
                        'title': "Equipment Type Code Table",
                        'url': "equipment_type",
                        'icon': "img/whales/equipment.svg",
                    },
                ]
            },
        ]

        return context


def par_delete(request, url, emm_id, prm_id):
    try:
        emm = models.EmmMakeModel.objects.get(emm_id=emm_id)
        prm = models.PrmParameterCode.objects.get(prm_id=prm_id)

        prm_obj = models.EprEquipmentParameters.objects.get(emm=emm, prm=prm)

        prm_obj.delete()

    finally:
        return HttpResponseRedirect(reverse("whalesdb:details_"+url, kwargs={'pk': emm_id}))


def ecp_delete(request, ecp_id):
    try:
        ecp = models.EcpChannelProperties.objects.get(ecp_id=ecp_id)
        emm_id = ecp.emm.emm_id
        ecp.delete()
    finally:
        return HttpResponseRedirect(reverse("whalesdb:details_recorder", kwargs={'pk': emm_id}))


class CloserTemplateView(TemplateView):
    template_name = 'whalesdb/close_me.html'


class CloserNoRefreshTemplateView(TemplateView):
    template_name = 'whalesdb/close_me_no_refresh.html'


class CreateTemplate(CreateView):
    template_name = "whalesdb/create_default.html"
    success_url = "#"
    cancel_url = "whalesdb:index"

    def get_initial(self):
        if 'pop' in self.kwargs:
            self.template_name = "whalesdb/create_default_no_head.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.cancel_url

        if 'pop' in self.kwargs:
            context["pop"] = True

        return context


class CreateDeploymentForm(CreateTemplate):
    form_class = forms.CreateDeploymentForm


class CreateMooringForm(CreateTemplate):
    form_class = forms.CreateMooringForm


class CreateStationForm(CreateTemplate):
    form_class = forms.CreateStationForm


class CreateProjectForm(CreateTemplate):
    form_class = forms.CreateProjectForm


class CreateCruiseForm(CreateTemplate):
    form_class = forms.CreateCruiseForm


class CreateStationEventForm(CreateTemplate):
    form_class = forms.CreateStationEventForm


class CreateRecordEventForm(CreateTemplate):
    form_class = forms.CreateRecordEventForm


class CreateRecordScheduleForm(CreateTemplate):
    form_class = forms.CreateRecordScheduleForm


class CreateRecordStageForm(CreateTemplate):
    form_class = forms.CreateRecordStageForm


class CreateTeamForm(CreateTemplate):
    form_class = forms.CreateTeamForm


class CreateMakeModel(CreateTemplate):
    form_class = forms.EmmMakeModelForm


class CreateParameter(CreateTemplate):
    form_class = forms.EprEquipmentParametersForm

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
        emm = models.EqrRecorderProperties.objects.get(pk=emm_id)

        ecp = models.EcpChannelProperties(emm=emm, ecp_channel_no=form.cleaned_data['ecp_channel_no'],
                                       eqa_adc_bits=form.cleaned_data['eqa_adc_bits'],
                                       ecp_voltage_range=form.cleaned_data['ecp_voltage_range'],
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


class CreateHydrophone(CreateEMM):
    form_class = forms.EqhHydrophonePropertiesForm
    success_url = "whalesdb:list_hydrophone"
    cancel_url = success_url

    def form_valid(self, form):
        emm = super().form_valid(form)

        eqh = models.EqhHydrophoneProperties(emm=emm,
                                                eqh_range_min=form.cleaned_data['eqh_range_min'],
                                                eqh_range_max=form.cleaned_data['eqh_range_max'])
        eqh.save()
        return HttpResponseRedirect(reverse('whalesdb:details_hydrophone', kwargs={'pk': eqh.pk}))


class CreateRecorder(CreateEMM):
    form_class = forms.EqrRecorderPropertiesForm
    cancel_url = "whalesdb:list_recorder"

    def form_valid(self, form):
        emm = super().form_valid(form)

        eqr = models.EqrRecorderProperties(emm=emm,
                                              eqc_max_channels=form.cleaned_data['eqc_max_channels'],
                                              eqc_max_sample_rate=form.cleaned_data['eqc_max_sample_rate'])
        eqr.save()

        return HttpResponseRedirect(reverse('whalesdb:details_recorder', kwargs={'pk': eqr.pk}))


class DetailsMakeModel(DetailView):
    template_name = "whalesdb/details_make_model.html"

    def get_emm(self):
        return models.EmmMakeModel.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['objects'] = []

        labels = forms.get_labels(models.EmmMakeModel)
        context['objects'].append({
            "object": kwargs['object'].emm,
            "fields": get_fields(labels)
        })

        labels = forms.get_short_labels(models.EprEquipmentParameters)
        context['parameter_fields'] = get_fields(labels)
        context['parameter'] = [p for p in models.EprEquipmentParameters.objects.filter(emm=self.get_emm())]

        return context


class DetailsRecorder(DetailsMakeModel):
    model = models.EqrRecorderProperties

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        labels = forms.get_labels(models.EqrRecorderProperties)
        context['objects'].append({
            "object": kwargs['object'],
            "fields": get_fields(labels)
        })

        labels = forms.get_short_labels(models.EcpChannelProperties)
        context['channel_fields'] = get_fields(labels)
        context['channels'] = [c for c in models.EcpChannelProperties.objects.filter(emm=kwargs['object'])]
        context['url'] = 'recorder'

        return context


class DetailsHydrophone(DetailsMakeModel):
    model = models.EqhHydrophoneProperties

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        labels = forms.get_labels(models.EqhHydrophoneProperties)
        context['objects'].append({
            "object": kwargs['object'],
            "fields": get_fields(labels)
        })
        context['url'] = 'hydrophone'

        return context


class ListGeneric(FilterView):
    template_name = 'whalesdb/filter_inventory.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        labels = forms.get_short_labels(self.model)
        context['fields'] = get_fields(labels)
        context['new_object'] = self.create_link
        context['detail_object'] = self.detail_link
        return context


class ListEMM(ListGeneric):

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['detail_type'] = 'emm'
        return context


class ListRecorder(ListEMM):
    model = models.EqrRecorderProperties
    filterset_class = filters.FilterRecorder
    create_link = "whalesdb:create_recorder"
    detail_link = "whalesdb:details_recorder"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        context["title"] = "Recorder Equipment"

        return context


class ListHydrophone(ListEMM):
    model = models.EqhHydrophoneProperties
    filterset_class = filters.FilterHydrophone
    create_link = "whalesdb:create_hydrophone"
    detail_link = "whalesdb:details_hydrophone"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        context["title"] = "Hydrophone Equipment"

        return context


class ListRecordEvent(ListGeneric):
    model = models.RecRecordingEvents
    filterset_class = filters.FilterRecordEvent
    create_link = "whalesdb:create_rec"
    detail_link = "whalesdb:list_rec"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        context["detail_type"] = 'rec'
        context["title"] = "Recording Event"

        return context


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


class CodeEditView(CreateView):

    template_name = "whalesdb/code_entry.html"
    form_class = forms.CodeEditForm

    def get_initial(self):
        obj_def = get_model_object(self.kwargs['lookup'])
        self.model = obj_def['model']
        self.form_class._meta.model = self.model

    def get_context_data(self, **kwargs):

        obj_def = get_model_object(self.kwargs['lookup'])

        context = super().get_context_data(**kwargs)
        context["title"] = obj_def['label']
        return context

    def form_valid(self, form):
        # save the form but don't commit changes. Get the value from the cleaned data array
        form.save(commit=False)

        obj_def = get_model_object(self.kwargs['lookup'])

        obj = obj_def['model'].objects.all().order_by('-' + obj_def['order']).values_list()

        n_id = 1
        if obj and obj[0][0]:
            n_id = int(obj[0][0]) + 1

        n_val = form.cleaned_data['value']

        n_obj = obj_def['model'](n_id, n_val)
        n_obj.save()

        return HttpResponseRedirect(reverse('whalesdb:close_me'))


class SetCodeEditView(CreateView):

    template_name = "whalesdb/code_entry.html"
    form_class = forms.CreateStationEventCodeForm

    def form_valid(self, form):
        # save the form but don't commit changes. Get the value from the cleaned data array
        form.save(commit=False)

        obj = models.SetStationEventCode.objects.all().order_by('-set_name').values_list()

        n_id = 1
        if obj and obj[0][0]:
            n_id = int(obj[0][0]) + 1

        n_val_name = form.cleaned_data['set_name']
        n_val_des = form.cleaned_data['set_description']

        n_obj = models.SetStationEventCode(n_id, n_val_name, n_val_des)
        n_obj.save()

        return HttpResponseRedirect(reverse('whalesdb:close_me'))
