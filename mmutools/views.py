from django.utils.translation import gettext as _

from lib.functions.custom_functions import listrify
from shared_models import models as shared_models
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Count, TextField, F, Sum
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView
from django_filters.views import FilterView
from . import models
from . import forms
from . import filters
from . import reports

class CloserTemplateView(TemplateView):
    template_name = 'mmutools/close_me.html'


def in_vault_group(user):
    if user:
        return True


class VaultAccessRequired(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_vault_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_vault_group, login_url='/accounts/denied/')
def index(request):
    return render(request, 'mmutools/index.html')

# #
# # INVENTORY #
# # ###########
# #
#
class ItemListView(VaultAccessRequired, FilterView):
    template_name = "mmutools/item_list.html"
    filterset_class = filters.ItemFilter
    queryset = models.Item.objects.annotate(
        search_term=Concat('id', 'unique_id', 'item_name', 'description', 'owner', 'size', 'container_space', 'category', 'gear_type', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Item.objects.first()
        context["field_list"] = [
            'id',
            'unique_id',
            'item_name',
            'description',
            'owner',
            'size',
            'container_space',
            'category',
            'gear_type',
        ]
        return context

class ItemDetailView(VaultAccessRequired, DetailView):
    model = models.Item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'unique_id',
            'item_name',
            'description',
            'owner',
            'size',
            'container_space',
            'category',
            'gear_type',

        ]
        return context



class ItemUpdateView(VaultAccessRequired, UpdateView):
    model = models.Item
    form_class = forms.ItemForm


    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Item record successfully updated for : {my_object}"))
        return super().form_valid(form)

class ItemCreateView(VaultAccessRequired, CreateView):
    model = models.Item
    form_class = forms.ItemForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Item record successfully created for : {my_object}"))
        return super().form_valid(form)

class ItemDeleteView(VaultAccessRequired, DeleteView):
    model = models.Item
    permission_required = "__all__"
    success_url = reverse_lazy('mmutools:item_list')
    success_message = 'The item was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    ##Quantities

class QuantityListView(VaultAccessRequired, FilterView):
    template_name = "mmutools/quantity_list.html"
    filterset_class = filters.QuantityFilter
    queryset = models.Quantity.objects.annotate(
        search_term=Concat('id', 'item', 'unique_id', 'serial_number', 'quantity_oh', 'quantity_lent', 'quantity_avail', 'quantity_oo', 'last_audited', 'last_audited_by', 'location_stored', 'bin_id', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Quantity.objects.first()
        context["field_list"] = [
            'id',
            'item',
            'unique_id',
            'serial_number',
            'quantity_oh',
            'quantity_lent',
            'quantity_avail',
            'quantity_oo',
            'last_audited',
            'last_audited_by',
            'location_stored',
            'bin_id',
        ]
        return context

class QuantityDetailView(VaultAccessRequired, DetailView):
    model = models.Quantity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'item',
            'unique_id',
            'serial_number',
            'quantity_oh',
            'quantity_lent',
            'quantity_avail',
            'quantity_oo',
            'last_audited',
            'last_audited_by',
            'location_stored',
            'bin_id',
        ]

        # for quantity in context['field_list']:
        #     quantity.quantity_avail = models.Quantity.objects.all().annotate(sum_oh=Sum('quantity_oh')).annotate(
        #         sum_lent=Sum('quantity_lent')).annotate(sum_diff=F('sum_oh') - F('sum_lent'))

        return context

 # Trying to define it so that I can return the available number of items (needs to add all inv for an item and subtract all lent out items)



class QuantityUpdateView(VaultAccessRequired, UpdateView):
    model = models.Quantity
    form_class = forms.QuantityForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Item record successfully updated for : {my_object}"))
        return super().form_valid(form)

class QuantityCreateView(VaultAccessRequired, CreateView):
    model = models.Quantity
    form_class = forms.QuantityForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Item record successfully created for : {my_object}"))
        return super().form_valid(form)

class QuantityDeleteView(VaultAccessRequired, DeleteView):
    model = models.Quantity
    permission_required = "__all__"
    success_url = reverse_lazy('mmutools:quantity_list')
    success_message = 'The item was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    ## PERSONNEL ##

class PersonnelListView(VaultAccessRequired, FilterView):
    template_name = "mmutools/personnel_list.html"
    filterset_class = filters.PersonnelFilter
    queryset = models.Personnel.objects.annotate(
        search_term=Concat('id', 'first_name', 'last_name', 'organisation', 'email', 'phone', 'exp_level', 'training', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Personnel.objects.first()
        context["field_list"] = [
            'id',
            'first_name',
            'last_name',
            'organisation',
            'email',
            'phone',
            'exp_level',
            'training',

        ]
        return context

class PersonnelDetailView(VaultAccessRequired, DetailView):
    model = models.Personnel

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'first_name',
            'last_name',
            'organisation',
            'email',
            'phone',
            'exp_level',
            'training',

        ]
        return context

class PersonnelUpdateView(VaultAccessRequired, UpdateView):
    model = models.Personnel
    form_class = forms.PersonnelForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Personnel record successfully updated for : {my_object}"))
        return super().form_valid(form)

class PersonnelCreateView(VaultAccessRequired, CreateView):
    model = models.Personnel
    form_class = forms.PersonnelForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Personnel record successfully created for : {my_object}"))
        return super().form_valid(form)

class PersonnelDeleteView(VaultAccessRequired, DeleteView):
    model = models.Personnel
    permission_required = "__all__"
    success_url = reverse_lazy('mmutools:personnel_list')
    success_message = 'The personnel file was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    ## SUPPLIER ##

class SupplierListView(VaultAccessRequired, FilterView):
    template_name = "mmutools/supplier_list.html"
    filterset_class = filters.SupplierFilter
    queryset = models.Supplier.objects.annotate(
        search_term=Concat('id', 'item', 'supplier', 'contact_number', 'email', 'last_invoice', 'last_purchased', 'last_purchased_by', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Supplier.objects.first()
        context["field_list"] = [
            'id',
            'item',
            'supplier',
            'contact_number',
            'email',
            'last_invoice',
            'last_purchased',
            'last_purchased_by',

        ]
        return context

class SupplierDetailView(VaultAccessRequired, DetailView):
    model = models.Supplier

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'item',
            'supplier',
            'contact_number',
            'email',
            'last_invoice',
            'last_purchased',
            'last_purchased_by',

        ]
        return context

class SupplierUpdateView(VaultAccessRequired, UpdateView):
    model = models.Supplier
    form_class = forms.SupplierForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Supplier record successfully updated for : {my_object}"))
        return super().form_valid(form)

class SupplierCreateView(VaultAccessRequired, CreateView):
    model = models.Supplier
    form_class = forms.SupplierForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Supplier record successfully created for : {my_object}"))
        return super().form_valid(form)

class SupplierDeleteView(VaultAccessRequired, DeleteView):
    model = models.Supplier
    permission_required = "__all__"
    success_url = reverse_lazy('mmutools:supplier_list')
    success_message = 'The supplier file was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    ## SUPPLIER FILE UPLOAD ##

class FileCreateView(VaultAccessRequired, CreateView):
    model = models.File
    template_name = 'mmutools/file_form_popout.html'
    form_class = forms.FileForm
    success_url = reverse_lazy('mmutools:close_me')

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse("mmutools:close_me"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["editable"] = True
        supplier = models.Supplier.objects.get(pk=self.kwargs.get('supplier'))
        context["supplier"] = supplier
        return context

    def get_initial(self):
        supplier = models.Supplier.objects.get(pk=self.kwargs['supplier'])
        return {
            'supplier': supplier,
        }


class FileUpdateView(VaultAccessRequired, UpdateView):
    model = models.File
    template_name = 'mmutools/file_form_popout.html'
    form_class = forms.FileForm


    def get_success_url(self, **kwargs):
        return reverse_lazy("mmutools:file_detail", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        context["editable"] = True
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy("mmutools:supplier_detail", kwargs={"pk": object.supplier.id}))

    def get_initial(self):
        supplier = models.Supplier.objects.get(pk=self.kwargs['supplier'])
        return {
            'supplier': supplier,
            'date_uploaded': timezone.now(),
        }

class FileDetailView(FileUpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["editable"] = False
        return context

def file_delete(request, pk):
    object = models.Supplier.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The file has been successfully deleted from the entry."))
    return HttpResponseRedirect(reverse_lazy("mmutools:file_detail", kwargs={"pk": object.object.id}))


    ## LENDING ##

class LendingListView(VaultAccessRequired, FilterView):
    template_name = "mmutools/lending_list.html"
    filterset_class = filters.LendingFilter
    queryset = models.Lending.objects.annotate(
        search_term=Concat('id', 'item', 'quantity_lent', 'lent_to', 'lent_date', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Lending.objects.first()
        context["field_list"] = [
            'id',
            'item',
            'quantity_lent',
            'lent_to',
            'lent_date',

        ]
        return context

class LendingDetailView(VaultAccessRequired, DetailView):
    model = models.Lending

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'item',
            'quantity_lent',
            'lent_to',
            'lent_date',

        ]
        return context

class LendingUpdateView(VaultAccessRequired, UpdateView):
    model = models.Lending
    form_class = forms.LendingForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Lending record successfully updated for : {my_object}"))
        return super().form_valid(form)

class LendingCreateView(VaultAccessRequired, CreateView):
    model = models.Lending
    form_class = forms.LendingForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Lending record successfully created for : {my_object}"))
        return super().form_valid(form)

class LendingDeleteView(VaultAccessRequired, DeleteView):
    model = models.Lending
    permission_required = "__all__"
    success_url = reverse_lazy('mmutools:lending_list')
    success_message = 'The lending agreement was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    ## INCIDENT ##

class IncidentListView(VaultAccessRequired, FilterView):
    template_name = "mmutools/incident_list.html"
    filterset_class = filters.IncidentFilter
    queryset = models.Incident.objects.annotate(
        search_term=Concat('id', 'species_count', 'submitted', 'first_report', 'location', 'region', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Incident.objects.first()
        context["field_list"] = [
            'id',
            'species_count',
            'submitted',
            'first_report',
            'location',
            'region',
            'incident_type',
            'exam',

        ]
        return context

class IncidentDetailView(VaultAccessRequired, DetailView):
    model = models.Incident

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'species_count',
            'submitted',
            'first_report',
            'lat',
            'long',
            'location',
            'region',
            'species',
            'sex',
            'age_group',
            'incident_type',
            'gear_presence',
            'gear_desc',
            'exam',
            'necropsy',
            'results',
            'photos',
            'data_folder',
            'comments',

        ]
        return context

class IncidentUpdateView(VaultAccessRequired, UpdateView):
    model = models.Incident
    form_class = forms.IncidentForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Incident record successfully updated for : {my_object}"))
        return super().form_valid(form)

class IncidentCreateView(VaultAccessRequired, CreateView):
    model = models.Incident
    form_class = forms.IncidentForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Incident record successfully created for : {my_object}"))
        return super().form_valid(form)

class IncidentDeleteView(VaultAccessRequired, DeleteView):
    model = models.Incident
    permission_required = "__all__"
    success_url = reverse_lazy('mmutools:incident_list')
    success_message = 'The incident file was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)