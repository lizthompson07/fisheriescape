from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.db.models import Value, TextField, Q
from django.db.models.functions import Concat
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
###
from lib.functions.fiscal_year import fiscal_year
from . import models
from . import forms
from . import filters


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'scifi/close_me.html'


def not_in_scifi_group(user):
    if user:
        return user.groups.filter(name='scifi_access').count() != 0


def not_in_scifi_admin_group(user):
    if user:
        return user.groups.filter(name='scifi_admin').count() != 0


class SciFiAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return not_in_scifi_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class SciFiAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return not_in_scifi_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)



class IndexTemplateView(SciFiAccessRequiredMixin, TemplateView):
    template_name = 'scifi/index.html'

# ALLOTMENT CODE #
##################

class AllotmentCodeListView(SciFiAccessRequiredMixin, ListView):
    model = models.AllotmentCode


class AllotmentCodeUpdateView(SciFiAccessRequiredMixin, UpdateView):
    model = models.AllotmentCode
    form_class = forms.AllotmentCodeForm
    success_url = reverse_lazy('scifi:allotment_list')


class AllotmentCodeCreateView(SciFiAccessRequiredMixin, CreateView):
    model = models.AllotmentCode
    form_class = forms.AllotmentCodeForm
    success_url = reverse_lazy('scifi:digestion_list')


class AllotmentCodeDeleteView(SciFiAccessRequiredMixin, DeleteView):
    model = models.AllotmentCode
    success_url = reverse_lazy('scifi:digestion_list')
    success_message = 'The allotment code was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class AllotmentCodeDetailView(SciFiAccessRequiredMixin, DetailView):
    model = models.AllotmentCode

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'code',
            'name',
        ]
        return context


# BUSINESS LINE #
#################

class BusinessLineListView(SciFiAccessRequiredMixin, ListView):
    model = models.BusinessLine


class BusinessLineUpdateView(SciFiAccessRequiredMixin, UpdateView):
    model = models.BusinessLine
    form_class = forms.BusinessLineForm
    success_url = reverse_lazy('scifi:business_list')


class BusinessLineCreateView(SciFiAccessRequiredMixin, CreateView):
    model = models.BusinessLine
    form_class = forms.BusinessLineForm
    success_url = reverse_lazy('scifi:business_list')


class BusinessLineDeleteView(SciFiAccessRequiredMixin, DeleteView):
    model = models.BusinessLine
    success_url = reverse_lazy('scifi:business_list')
    success_message = 'The business line was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class BusinessLineDetailView(SciFiAccessRequiredMixin, DetailView):
    model = models.BusinessLine

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'code',
            'name',
        ]
        return context

# LINE OBJECT #
###############

class LineObjectListView(SciFiAccessRequiredMixin, FilterView):
    template_name = 'scifi/lineobject_list.html'
    filterset_class = filters.LineObjectFilter
    model = models.LineObject
    queryset = models.LineObject.objects.annotate(
        search_term=Concat('code', 'name_eng', 'description_eng', output_field=TextField()))


class LineObjectUpdateView(SciFiAccessRequiredMixin, UpdateView):
    model = models.LineObject
    form_class = forms.LineObjectForm
    success_url = reverse_lazy('scifi:lo_list')


class LineObjectCreateView(SciFiAccessRequiredMixin, CreateView):
    model = models.LineObject
    form_class = forms.LineObjectForm
    success_url = reverse_lazy('scifi:lo_list')


class LineObjectDeleteView(SciFiAccessRequiredMixin, DeleteView):
    model = models.LineObject
    success_url = reverse_lazy('scifi:lo_list')
    success_message = 'The line object was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class LineObjectDetailView(SciFiAccessRequiredMixin, DetailView):
    model = models.LineObject

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'code',
            'name_eng',
            'description_eng',
        ]
        return context

# RC #
######

class ResponsibilityCentreListView(SciFiAccessRequiredMixin, ListView):
    model = models.ResponsibilityCenter


class ResponsibilityCentreUpdateView(SciFiAccessRequiredMixin, UpdateView):
    model = models.ResponsibilityCenter
    form_class = forms.ResponsibilityCentreForm
    success_url = reverse_lazy('scifi:rc_list')


class ResponsibilityCentreCreateView(SciFiAccessRequiredMixin, CreateView):
    model = models.ResponsibilityCenter
    form_class = forms.ResponsibilityCentreForm
    success_url = reverse_lazy('scifi:rc_list')


class ResponsibilityCentreDeleteView(SciFiAccessRequiredMixin, DeleteView):
    model = models.ResponsibilityCenter
    success_url = reverse_lazy('scifi:rc_list')
    success_message = 'The RC was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class ResponsibilityCentreDetailView(SciFiAccessRequiredMixin, DetailView):
    model = models.ResponsibilityCenter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'code',
            'name',
            'responsible_manager',
        ]
        return context


# PROJECT #
###########

class ProjectListView(SciFiAccessRequiredMixin, FilterView):
    filterset_class = filters.LineObjectFilter
    template_name = 'scifi/project_list.html'
    queryset = models.Project.objects.annotate(
        search_term=Concat('code', 'name', 'description', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name',
            'code',
            'description',
            'project_lead',
            'responsibility_center',
            'default_allotment_code',
            'default_business_line',
            'default_line_object',
        ]
        return context


class ProjectUpdateView(SciFiAccessRequiredMixin, UpdateView):
    model = models.Project
    form_class = forms.ProjectForm
    success_url = reverse_lazy('scifi:project_list')


class ProjectCreateView(SciFiAccessRequiredMixin, CreateView):
    model = models.Project
    form_class = forms.ProjectForm
    success_url = reverse_lazy('scifi:project_list')


class ProjectDeleteView(SciFiAccessRequiredMixin, DeleteView):
    model = models.Project
    success_url = reverse_lazy('scifi:project_list')
    success_message = 'The project was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class ProjectDetailView(SciFiAccessRequiredMixin, DetailView):
    model = models.ResponsibilityCenter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name',
            'code',
            'description',
            'project_lead',
            'responsibility_center',
            'default_allotment_code',
            'default_business_line',
            'default_line_object',
        ]
        return context


# TRANSACTION #
###############

class TransactionListView(SciFiAccessRequiredMixin, FilterView):
    template_name = 'scifi/transaction_list.html'
    filterset_class = filters.TransactionFilter
    model = models.Transaction
    # paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'fiscal_year',
            'transaction_type',
            'requisition_date',
            'obligation_cost',
            'supplier_description',
            'project.code',
            'invoice_date',
            'invoice_cost',
            'allotment_code.code',
            'business_line.code',
            'line_object.code',
            'in_mrs',
            'reference_number',
            'amount_paid_in_mrs',
            'mrs_notes',
            'procurement_hub_contact',
            'comment',
        ]
        context["my_object"] = self.model.objects.first()
        return context

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {
                "fiscal_year": fiscal_year(),
             }
        return kwargs


class TransactionDetailView(SciFiAccessRequiredMixin, DetailView):
    model = models.Transaction

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'transaction_type',
            'supplier_description',
            'project',
            'allotment_code',
            'business_line',
            'line_object',
            'requisition_date',
            'invoice_date',
            'obligation_cost',
            'invoice_cost',
            'in_mrs',
            'reference_number',
            'amount_paid_in_mrs',
            'mrs_notes',
            'procurement_hub_contact',
            'comment',
            'fiscal_year',
        ]
        return context


class TransactionUpdateView(SciFiAccessRequiredMixin, UpdateView):
    model = models.Transaction
    form_class = forms.TransactionForm


class TransactionCreateView(SciFiAccessRequiredMixin, CreateView):
    model = models.Transaction
    form_class = forms.TransactionForm


class TransactionDeleteView(SciFiAccessRequiredMixin, DeleteView):
    model = models.Transaction
    success_url = reverse_lazy('scifi:trans_list')
    success_message = 'The transaction was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
