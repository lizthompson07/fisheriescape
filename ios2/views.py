from django.shortcuts import render


from django.http import HttpResponse
from django.template import loader

# from .models import Question

import datetime
import os
import pandas as pd
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
from easy_pdf.views import PDFTemplateView
from lib.functions.fiscal_year import fiscal_year
from lib.functions.nz import nz
from . import models
from . import forms
from . import filters
# from . import reports
from shared_models import models as shared_models


# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     template = loader.get_template('ios2/index.html')
#     context = {
#         'latest_question_list': latest_question_list,
#     }
#     return HttpResponse(template.render(context, request))
# TYPE_CHOICES = [('CTD', 'CTD'), ('ADCP', 'ADCP')]

instrument_field_list = [
    'id',
    'instrument_type',
    'serial_number',
    'purchase_date',
    'project_title',
    'date_of_last_service',
    'date_of_next_service',
    # 'section',
    # 'program',
    # 'responsibility_center',
    # 'allotment_code',
    # 'existing_project_code',
    # 'status',
    # 'approved',
    # 'start_date',
    # 'end_date',
    # 'description_html',
    # 'priorities_html',
    # 'deliverables_html',
    # 'data_collection',
    # 'data_sharing',
    # 'data_storage',
    # 'metadata_url',
    # 'regional_dm',
    # 'regional_dm_needs',
    # 'sectional_dm',
    # 'sectional_dm_needs',
    # 'vehicle_needs',
    # 'it_needs',
    # 'chemical_needs',
    # 'ship_needs',
    # 'date_last_modified',
    # 'last_modified_by',
]

# Create your views here.


class CloserTemplateView(TemplateView):
    template_name = 'ios2/close_me.html'


class IndexTemplateView(TemplateView):
    template_name = 'ios2/index.html'


class InstrumentListView(LoginRequiredMixin, FilterView):
    login_url = '/accounts/login_required/'
    template_name = 'ios2/instrument_list.html'
    model = models.Instrument
    filterset_class = filters.InstrumentFilter


class MooringListView(LoginRequiredMixin, FilterView):
    login_url = '/accounts/login_required/'
    template_name = 'ios2/mooring_list.html'
    model = models.Deployment
    filterset_class = filters.DeploymentFilter


class InstrumentCreateView(LoginRequiredMixin, CreateView):
    model = models.Instrument
    login_url = '/accounts/login_required/'
    form_class = forms.NewInstrumentForm

    def form_valid(self, form):
        object = form.save()
        # models.Staff.objects.create(project=object, lead=True, employee_type_id=1, user_id=self.request.user.id)

        # for obj in models.OMCategory.objects.all():
        #     new_item = models.OMCost.objects.create(project=object, om_category=obj)
        #     new_item.save()

        return HttpResponseRedirect(reverse_lazy("ios2:instrument_detail", kwargs={"pk": object.id}))

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class InstrumentDetailView(LoginRequiredMixin, DetailView):
    model = models.Instrument
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrument = self.object
        context["field_list"] = [
            # 'id',
            'instrument_type',
            'serial_number',
            'purchase_date',
            'project_title',
            'date_of_last_service',
            'date_of_next_service',
            # 'section',
            # 'program',
            # 'coding|' + _("budget code"),
            # 'date_last_modified',
            # 'last_modified_by',
        ]

        # context["field_list_1"] = [
        #     'description_html',
        #     'priorities_html',
        #     'deliverables_html',
        # ]

        # bring in financial summary data
        # my_context = financial_summary_data(project)
        # context = {**my_context, **context}
        #
        # if not can_delete(self.request.user, project):
        #     context["report_mode"] = True
        context["report_mode"] = False
        return context


class InstrumentSubmitUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Instrument
    login_url = '/accounts/login_required/'
    form_class = forms.InstrumentSubmitForm
    template_name = "ios2/instrument_submit_form.html"

    def get_initial(self):
        if self.object.submitted:
            submit = False
        else:
            submit = True

        return {
            'last_modified_by': self.request.user,
            'submitted': submit,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        context["field_list"] = instrument_field_list
        context["report_mode"] = True

        # bring in financial summary data
        # my_context = financial_summary_data(project)
        # context = {**my_context, **context}

        return context


class InstrumentPrintDetailView(LoginRequiredMixin, PDFTemplateView):
    model = models.Instrument
    login_url = '/accounts/login_required/'
    template_name = "ios2/instrument_report.html"

    def get_pdf_filename(self):
        instrument = models.Instrument.objects.get(pk=self.kwargs["pk"])
        pdf_filename = "{}-{}-{}-{}-{}.pdf".format(
            instrument.year.id,
            instrument.section.division.abbrev,
            instrument.section.abbrev,
            instrument.id,
            str(instrument.project_title).title().replace(" ", "")[:10],
        )

        return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrument = models.Instrument.objects.get(pk=self.kwargs["pk"])
        context["report_mode"] = True
        context["object"] = instrument
        context["field_list"] = instrument_field_list

        # bring in financial summary data
        # my_context = financial_summary_data(project)
        # context = {**my_context, **context}

        return context


class InstrumentDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Instrument
    permission_required = "__all__"
    success_url = reverse_lazy('ios2:instrument_list')
    success_message = _('The instrument was successfully deleted!')
    login_url = '/accounts/login_required/'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class InstrumentUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Instrument
    login_url = '/accounts/login_required/'
    form_class = forms.InstrumentForm

    def get_initial(self):
        my_dict = {
            'last_modified_by': self.request.user,
        }

        try:
            my_dict["start_date"] = "{}-{:02d}-{:02d}".format(self.object.start_date.year, self.object.start_date.month,
                                                              self.object.start_date.day)
        except:
            print("no start date...")

        try:
            my_dict["end_date"] = "{}-{:02d}-{:02d}".format(self.object.end_date.year, self.object.end_date.month,
                                                            self.object.end_date.day)
        except:
            print("no end date...")

        return my_dict




# Deployments #
############


class DeploymentCreateView(LoginRequiredMixin, CreateView):
    model = models.Deployment
    template_name = 'ios2/deployment_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.DeploymentForm

    def get_initial(self):
        instrument = models.Instrument.objects.get(pk=self.kwargs['instrument'])
        return {
            'instrument': instrument,
        }

    def get_context_data(self, **kwargs):
        print(self.kwargs)
        # input('aaa?')
        context = super().get_context_data(**kwargs)
        # instrument = models.Instrument.objects.get(id=self.kwargs['instrument_type'])
        instrument = models.Instrument.objects.get(id=self.kwargs['instrument'])
        # instrument = models.Instrument.objects.all
        context['instrument'] = instrument.serial_number
        # context['object'] = self.object
        # context["field_list"] = ['mooring', 'mooring_number']
        context['cost_type'] = "deployment"
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ios2:close_me'))


class DeploymentUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Deployment
    template_name = 'ios2/deployment_form_popout.html'
    form_class = forms.DeploymentForm
    login_url = '/accounts/login_required/'

    # def get_initial(self):
    #     instrument = models.Instrument.objects.get(pk=self.kwargs['instrument'])
    #     return {
    #         'instrument': instrument,
    #     }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # instrument = models.Instrument.objects.get(id=self.kwargs['instrument'])
        context['instrument'] = self.object.instruments
        context['mooring_number'] = self.object.mooring_number
        context["field_list"] = ['mooring', 'mooring_number']
        context['cost_type'] = "deployment"
        # instrument = models.Instrument.objects.get(kwargs={"pk": pk})
        # context['instrument'] = instrument
        # context['object'] = self.object
        # context['cost_type'] = _("O&M")
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ios2:close_me'))


def deployment_delete(request, pk):
    object = models.Deployment.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The deployment has been successfully deleted."))
    return HttpResponseRedirect(reverse_lazy("ios2:instrument_detail", kwargs={"pk": object.instrument.id}))


def deployment_clear(request, instrument):
    instrument = models.Instrument.objects.get(pk=instrument)
    # for obj in models.Deployment.objects.all():
        # for cost in models.Deployment.objects.filter(project=project, om_category=obj):
        #     print(cost)
        #     if (cost.budget_requested is None or cost.budget_requested == 0) and not cost.description:
        #         cost.delete()

    messages.success(request, _("All empty O&M lines have been cleared."))
    return HttpResponseRedirect(reverse_lazy("ios2:instrument_detail", kwargs={"pk": instrument.id}))


def deployment_populate(request, instrument):
    instrument = models.Instrument.objects.get(pk=instrument)
    # for obj in models.OMCategory.objects.all():
    #     if not models.OMCost.objects.filter(project=project, om_category=obj).count():
    #         new_item = models.OMCost.objects.create(project=project, om_category=obj)
    #         new_item.save()

    messages.success(request, _("All O&M categories have been added to this project."))
    return HttpResponseRedirect(reverse_lazy("ios2:instrument_detail", kwargs={"pk": instrument.id}))




class DeploymentDetailView(LoginRequiredMixin, DetailView):
    model = models.Deployment
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrument = self.object
        context["field_list"] = [
            # 'id',
            'instrument',
            'instruments',
            'mooring',
            'mooring_number',
            'deploy_time',
            'recover_time',
            'depth',
            'lat',
            'lon',
            'comments'
            # 'instrument_type',
            # 'serial_number',
            # 'purchase_date',
            # 'project_title',
            # 'date_of_last_service',
            # 'date_of_next_service',
            # 'section',
            # 'program',
            # 'coding|' + _("budget code"),
            # 'date_last_modified',
            # 'last_modified_by',
        ]

        # context["field_list_1"] = [
        #     'description_html',
        #     'priorities_html',
        #     'deliverables_html',
        # ]

        # bring in financial summary data
        # my_context = financial_summary_data(project)
        # context = {**my_context, **context}
        #
        # if not can_delete(self.request.user, project):
        #     context["report_mode"] = True
        context["report_mode"] = False
        return context



# Deployments #
############

class InstrumentDeploymentCreateView(LoginRequiredMixin, CreateView):
    model = models.InstrumentDeployment
    template_name = 'ios2/instrudeployment_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.InstrumentDeploymentForm

    def get_initial(self):
        instrument = models.Instrument.objects.get(pk=self.kwargs['instrument'])
        return {
            'instrument': instrument,
        }

    def get_context_data(self, **kwargs):
        print(self.kwargs)
        # input('aaa?')
        context = super().get_context_data(**kwargs)
        # instrument = models.Instrument.objects.get(id=self.kwargs['instrument_type'])
        instrument = models.Instrument.objects.get(id=self.kwargs['instrument'])
        # instrument = models.Instrument.objects.all
        context['instrument'] = instrument.serial_number
        # context['object'] = self.object
        # context["field_list"] = ['mooring', 'mooring_number']
        context['cost_type'] = "deployment"
        context['field_list'] = ['instrument', 'deployment']
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ios2:close_me'))


class InstrumentDeploymentUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Deployment
    template_name = 'ios2/deployment_form_popout.html'
    form_class = forms.DeploymentForm
    login_url = '/accounts/login_required/'

    # def get_initial(self):
    #     instrument = models.Instrument.objects.get(pk=self.kwargs['instrument'])
    #     return {
    #         'instrument': instrument,
    #     }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # instrument = models.Instrument.objects.get(id=self.kwargs['instrument'])
        context['instrument'] = self.object.instruments
        context['mooring_number'] = self.object.mooring_number
        context["field_list"] = ['mooring', 'mooring_number']
        context['cost_type'] = "deployment"
        # instrument = models.Instrument.objects.get(kwargs={"pk": pk})
        # context['instrument'] = instrument
        # context['object'] = self.object
        # context['cost_type'] = _("O&M")
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ios2:close_me'))


def instrudeployment_delete(request, pk):
    object = models.Deployment.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The deployment has been successfully deleted."))
    return HttpResponseRedirect(reverse_lazy("ios2:instrument_detail", kwargs={"pk": object.instrument.id}))


def instrudeployment_clear(request, instrument):
    instrument = models.Instrument.objects.get(pk=instrument)
    # for obj in models.Deployment.objects.all():
        # for cost in models.Deployment.objects.filter(project=project, om_category=obj):
        #     print(cost)
        #     if (cost.budget_requested is None or cost.budget_requested == 0) and not cost.description:
        #         cost.delete()

    messages.success(request, _("All empty O&M lines have been cleared."))
    return HttpResponseRedirect(reverse_lazy("ios2:instrument_detail", kwargs={"pk": instrument.id}))


def instrudeployment_populate(request, instrument):
    instrument = models.Instrument.objects.get(pk=instrument)
    # for obj in models.OMCategory.objects.all():
    #     if not models.OMCost.objects.filter(project=project, om_category=obj).count():
    #         new_item = models.OMCost.objects.create(project=project, om_category=obj)
    #         new_item.save()

    messages.success(request, _("All O&M categories have been added to this project."))
    return HttpResponseRedirect(reverse_lazy("ios2:instrument_detail", kwargs={"pk": instrument.id}))




class InstrumentDeploymentDetailView(LoginRequiredMixin, DetailView):
    model = models.Deployment
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrument = self.object
        context["field_list"] = [
            # 'id',
            'instrument',
            'instruments',
            'mooring',
            'mooring_number',
            'deploy_time',
            'recover_time',
            'depth',
            'lat',
            'lon',
            'comments'
            # 'instrument_type',
            # 'serial_number',
            # 'purchase_date',
            # 'project_title',
            # 'date_of_last_service',
            # 'date_of_next_service',
            # 'section',
            # 'program',
            # 'coding|' + _("budget code"),
            # 'date_last_modified',
            # 'last_modified_by',
        ]

        # context["field_list_1"] = [
        #     'description_html',
        #     'priorities_html',
        #     'deliverables_html',
        # ]

        # bring in financial summary data
        # my_context = financial_summary_data(project)
        # context = {**my_context, **context}
        #
        # if not can_delete(self.request.user, project):
        #     context["report_mode"] = True
        context["report_mode"] = False
        return context
