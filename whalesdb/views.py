from django.views.generic import TemplateView, CreateView, ListView
from django.http import HttpResponseRedirect
from django_filters.views import FilterView

from . import forms
from . import models
from . import filters

def get_model_object(obj_name):
    obj_def = {}
    if obj_name == 'adcbits':
        obj_def = {
            'label': "ADC-Bits",
            'url': obj_name,
            'order': "eqa_id",
            'model': models.EqaAdcBitsCode
        }
    elif obj_name == 'parameter':
        obj_def = {
            'label': "Equipment Parameter",
            'url': obj_name,
            'order': "prm_id",
            'model': models.PrmParameterCode
        }
    elif obj_name == 'equipment_type':
        obj_def = {
            'label': "Equipment Type",
            'url': obj_name,
            'order': "eqt_id",
            'model': models.EqtEquipmentTypeCode
        }

    return obj_def


class AfterDeploymentForm(CreateView):
    model = models.DepDeployments
    fields = []

class IndexView(TemplateView):
    template_name = 'whalesdb/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['deployment'] = [
            {
                'title': "After Deployment",
                'url': "whalesdb:create_afterdep",
                'icon': "img/whales/hydrophone_inventory.svg",
            },
        ]

        context['data_inventory'] = [
            {
                'title': "Hydrophone Inventory",
                'url': "whalesdb:list_hydrophone",
                'icon': "img/whales/hydrophone_inventory.svg",
            },
        ]
        context['data_entry'] = [
            {
                'title': "Make and Model",
                'url': "whalesdb:create_makemodel",
                'icon': "img/whales/makemodel.svg",
            },
            {
                'title': "Hydrophone",
                'url': "whalesdb:create_hydrophone",
                'icon': "img/whales/microphone.svg",
            },
        ]
        context['code_list'] = [
            {
                'title': "ADC Bits Code Table",
                'url': "adcbits",
                'icon': "img/whales/transfer.svg",
            },
            {
                'title': "Parameter Code Table",
                'url': "parameter",
                'icon': "img/whales/function.svg",
            },
            {
                'title': "Equipment Type Code Table",
                'url': "equipment_type",
                'icon': "img/whales/equipment.svg",
            },
        ]
        return context


class CloserTemplateView(TemplateView):
    template_name = 'whalesdb/close_me.html'


class CreateMakeModel(CreateView):
    template_name = 'whalesdb/create_makemodel.html'
    model = models.EmmMakeModel
    fields = ['eqt', 'emm_make', 'emm_model', 'emm_depth_rating', 'emm_description']

    def get_success_url(self):
        return ""


class CreateHydrophone(CreateView):
    template_name = 'whalesdb/create_hydrophone.html'
    model = models.EqhHydrophoneProperties
    fields = ['emm', 'eqh_range_max', 'eqh_range_min']

    def get_success_url(self):
        return ""


class ListViewHydrophone(FilterView):
    template_name = 'whalesdb/filter_inventory.html'
    model = models.EqhHydrophoneProperties
    filterset_class = filters.FilterHydrophone


class CodeListView(ListView):
    template_name = "whalesdb/code_list.html"
    model = models.EqaAdcBitsCode

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['lookup'] = get_model_object(self.kwargs['lookup'])
        self.model = context['lookup']['model']
        context["code_list"] = self.model.objects.all().order_by(context['lookup']['order']).values_list()

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

        n_val = form.cleaned_data['value']
        n_id = 1
        if obj and obj[0][0]:
            n_id = int(obj[0][0]) + 1

        n_obj = obj_def['model'](n_id, n_val)
        n_obj.save()

        return HttpResponseRedirect('')
