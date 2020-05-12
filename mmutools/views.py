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
from django.utils import timezone
from . import models
from . import forms
from . import filters
from . import reports


class CloserTemplateView(TemplateView):
    template_name = 'mmutools/close_me.html'

### Permissions ###

class MmutoolsAccessRequired(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)

def in_mmutools_admin_group(user):
    if "mmutools_admin" in [g.name for g in user.groups.all()]:
        return True

class MmutoolsAdminAccessRequired(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_mmutools_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


def in_mmutools_edit_group(user):
    """this group includes the admin group so there is no need to add an admin to this group"""
    if user:
        if in_mmutools_admin_group(user) or user.groups.filter(name='mmutools_edit').count() != 0:
            return True

class MmutoolsEditRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_mmutools_edit_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


@login_required(login_url='/accounts/login_required/')
def index(request):
    return render(request, 'mmutools/index.html')


# #
# # INVENTORY #
# # ###########
# #
#
class ItemListView(MmutoolsAccessRequired, FilterView):
    template_name = "mmutools/item_list.html"
    filterset_class = filters.SpecificItemFilter
    queryset = models.Item.objects.annotate(
        search_term=Concat('id', 'item_name', 'description', 'serial_number', 'owners', 'sizes', 'categories',
                           'gear_types', 'last_purchased', 'last_purchased_by', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Item.objects.first()
        context["field_list"] = [
            'id',
            'tname|{}'.format(_("Item name (size)")),
            'description',
            'serial_number',
            'owners',
            # 'sizes',
            'categories',
            'gear_types',
            'suppliers',
            'last_purchased',
            'last_purchased_by',
        ]
        return context


class ItemDetailView(MmutoolsAccessRequired, DetailView):
    model = models.Item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'item_name',
            'description',
            'serial_number',
            'owners',
            'sizes',
            'categories',
            'gear_types',
            'suppliers',
            'last_purchased',
            'last_purchased_by',

        ]

        # contexts for _quantity.html file
        context["random_qty"] = models.Quantity.objects.first()
        context["qty_field_list"] = [
            'quantity',
            'statuses',
            'locations',
            'bin_id',
        ]

               # now when you create a new item you get this error:   context['quantity_avail'] = ohqty - lentqty
        # TypeError: unsupported operand type(s) for -: 'NoneType' and 'NoneType' -- have to add a case where there is
        # no info yet in those fields? -- fixed it I think~!!! WOOOOH

        ohqty = self.get_object().quantities.filter(statuses=1).aggregate(dsum=Sum('quantity')).get('dsum')
        lentqty = self.get_object().quantities.filter(statuses=3).aggregate(dsum=Sum('quantity')).get('dsum')

        if ohqty is None:
            ohqty = 0
        else:
            ohqty = ohqty

        if lentqty is None:
            lentqty = 0
        else:
            lentqty = lentqty

        context['quantity_avail'] = ohqty - lentqty

        # context for _supplier.html
        context["random_sup"] = models.Supplier.objects.first()
        context["sup_field_list"] = [
            'supplier_name',
            'contact_number',
            'email',

        ]


        # context for _lending.html
        context["random_lend"] = models.Quantity.objects.first()
        context["lend_field_list"] = [
            'lent_to',
            'quantity',
            'lent_date',
            'return_date',
        ]

        # context for _files.html
        context["random_file"] = models.File.objects.first()
        context["file_field_list"] = [
            'caption',
            'file',
            'date_uploaded',
        ]

        return context


class ItemUpdateView(MmutoolsEditRequiredMixin, UpdateView):
    model = models.Item
    form_class = forms.ItemForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Item record successfully updated for : {my_object}"))
        return super().form_valid(form)


class ItemCreateView(MmutoolsEditRequiredMixin, CreateView):
    model = models.Item
    form_class = forms.ItemForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Item record successfully created for : {my_object}"))
        return super().form_valid(form)


class ItemDeleteView(MmutoolsEditRequiredMixin, DeleteView):
    model = models.Item
    permission_required = "__all__"
    success_url = reverse_lazy('mmutools:item_list')
    success_message = 'The item was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

        ## LOCATION ##

class LocationListView(MmutoolsAdminAccessRequired, FilterView):
    template_name = "mmutools/location_list.html"
    filterset_class = filters.LocationFilter
    queryset = models.Location.objects.annotate(
        search_term=Concat('id', 'location', 'address', 'container', 'container_space',
                           output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Location.objects.first()
        context["field_list"] = [
            'id',
            'location',
            'address',
            'container',
            'container_space',

        ]
        return context

class LocationDetailView(MmutoolsAdminAccessRequired, DetailView):
    model = models.Location

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'location',
            'address',
            'container',
            'container_space',

        ]
        return context

class LocationUpdateView(MmutoolsAdminAccessRequired, UpdateView):
    model = models.Location
    form_class = forms.LocationForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Location record successfully updated for : {my_object}"))
        return super().form_valid(form)

class LocationCreateView(MmutoolsAdminAccessRequired, CreateView):
    model = models.Location
    form_class = forms.LocationForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Location record successfully created for : {my_object}"))
        return super().form_valid(form)

class LocationDeleteView(MmutoolsAdminAccessRequired, DeleteView):
    model = models.Location
    permission_required = "__all__"
    success_url = reverse_lazy('mmutools:location_list')
    success_message = 'The location file was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    ##Quantities


class QuantityListView(MmutoolsAccessRequired, FilterView):
    template_name = "mmutools/quantity_list.html"
    filterset_class = filters.QuantityFilter
    queryset = models.Quantity.objects.annotate(
        search_term=Concat('id', 'items', 'quantity', 'statuses', 'lent_to', 'lent_date', 'return_date', 'last_audited', 'last_audited_by', 'locations', 'bin_id',
                           output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Quantity.objects.first()
        context["field_list"] = [
            'id',
            'items',
            'quantity',
            'statuses',
            'lent_to',
            'lent_date',
            'return_date',
            'last_audited',
            'last_audited_by',
            'locations',
            'bin_id',
        ]
        return context


class QuantityDetailView(MmutoolsAccessRequired, DetailView):
    model = models.Quantity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'items',
            'quantity',
            'statuses',
            'lent_to',
            'lent_date',
            'return_date',
            'last_audited',
            'last_audited_by',
            'locations',
            'bin_id',
        ]

        return context


class QuantityUpdateView(MmutoolsEditRequiredMixin, UpdateView):
    model = models.Quantity
    form_class = forms.QuantityForm

    def get_template_names(self):
       return "mmutools/quantity_form_popout.html" if self.kwargs.get("pop") else "mmutools/quantity_form.html"

    def get_form_class(self):
        return forms.QuantityForm1 if self.kwargs.get("pop") else forms.QuantityForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Quantity record successfully updated for : {my_object}"))
        success_url = reverse_lazy('shared_models:close_me') if self.kwargs.get("pop") else reverse_lazy('mmutools:quantity_detail', kwargs={"pk": my_object.id})
        return HttpResponseRedirect(success_url)


class QuantityCreateView(MmutoolsEditRequiredMixin, CreateView):
    model = models.Quantity
    form_class = forms.QuantityForm

    def get_template_names(self):
       return "mmutools/quantity_form_popout.html" if self.kwargs.get("pk") else "mmutools/quantity_form.html"

    def get_form_class(self):
        return forms.QuantityForm1 if self.kwargs.get("pk") else forms.QuantityForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Quantity record successfully created for : {my_object}"))
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me') if self.kwargs.get("pk") else reverse_lazy('mmutools:quantity_list'))


    def get_initial(self):
        return {'items': self.kwargs.get('pk')}


class QuantityDeleteView(MmutoolsEditRequiredMixin, DeleteView):
    model = models.Quantity
    permission_required = "__all__"
    success_message = 'The quantity was successfully deleted!'

    def get_template_names(self):
        return "mmutools/generic_confirm_delete_popout.html" if self.kwargs.get("pop") else "mmutools/quantity_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        my_object = self.get_object()
        my_object.delete()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me') if self.kwargs.get("pop") else reverse_lazy('mmutools:quantity_list'))


    ## PERSONNEL ##


class PersonnelListView(MmutoolsAdminAccessRequired, FilterView):
    template_name = "mmutools/personnel_list.html"
    filterset_class = filters.PersonnelFilter
    queryset = models.Personnel.objects.annotate(
        search_term=Concat('id', 'first_name', 'last_name', 'organisation', 'email', 'phone', 'exp_level', 'training',
                           output_field=TextField()))

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


class PersonnelDetailView(MmutoolsAdminAccessRequired, DetailView):
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


class PersonnelUpdateView(MmutoolsAdminAccessRequired, UpdateView):
    model = models.Personnel
    form_class = forms.PersonnelForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Personnel record successfully updated for : {my_object}"))
        return super().form_valid(form)


class PersonnelCreateView(MmutoolsAdminAccessRequired, CreateView):
    model = models.Personnel
    form_class = forms.PersonnelForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Personnel record successfully created for : {my_object}"))
        return super().form_valid(form)


class PersonnelDeleteView(MmutoolsAdminAccessRequired, DeleteView):
    model = models.Personnel
    permission_required = "__all__"
    success_url = reverse_lazy('mmutools:personnel_list')
    success_message = 'The personnel file was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    ## SUPPLIER ##


class SupplierListView(MmutoolsAccessRequired, FilterView):
    template_name = "mmutools/supplier_list.html"
    filterset_class = filters.SupplierFilter
    queryset = models.Supplier.objects.annotate(
        search_term=Concat('id', 'supplier_name', 'contact_number', 'email', 'website', 'comments',
                           output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Supplier.objects.first()
        context["field_list"] = [
            'id',
            'supplier_name',
            'contact_number',
            'email',
            'website',
            'comments',

        ]
        return context


class SupplierDetailView(MmutoolsAccessRequired, DetailView):
    model = models.Supplier

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'supplier_name',
            'contact_number',
            'email',
            'website',
            'comments',
        ]
        return context


class SupplierUpdateView(MmutoolsEditRequiredMixin, UpdateView):
    model = models.Supplier
    form_class = forms.SupplierForm

    def get_template_names(self):
       return "mmutools/supplier_form_popout.html" if self.kwargs.get("pop") else "mmutools/supplier_form.html"

    def get_form_class(self):
        return forms.SupplierForm1 if self.kwargs.get("pop") else forms.SupplierForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Supplier record successfully updated for : {my_object}"))
        success_url = reverse_lazy('shared_models:close_me') if self.kwargs.get("pop") else reverse_lazy('mmutools:supplier_detail', kwargs={"pk": my_object.id})
        return HttpResponseRedirect(success_url)

class SupplierCreateView(MmutoolsEditRequiredMixin, CreateView):
    model = models.Supplier
    form_class = forms.SupplierForm

    def get_template_names(self):
       return "mmutools/supplier_form_popout.html" if self.kwargs.get("pk") else "mmutools/supplier_form.html"

    def get_form_class(self):
        return forms.SupplierForm1 if self.kwargs.get("pk") else forms.SupplierForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Supplier record successfully created for : {my_object}"))
        #if there's a pk argumentm this means user is calling from item_detail page and

        if self.kwargs.get("pk"):
            my_item = models.Item.objects.get(pk=self.kwargs.get("pk"))
            my_item.suppliers.add(my_object)
            return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))
        else:
            return HttpResponseRedirect(reverse_lazy('mmutools:supplier_list'))

    def get_initial(self):
        return {'item': self.kwargs.get('pk')}

class SupplierDeleteView(MmutoolsEditRequiredMixin, DeleteView):
    model = models.Supplier
    permission_required = "__all__"
    success_message = 'The supplier file was successfully deleted!'

    def get_template_names(self):
        return "mmutools/generic_confirm_delete_popout.html" if self.kwargs.get("pop") else "mmutools/supplier_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        my_object = self.get_object()
        my_object.delete()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me') if self.kwargs.get("pop") else reverse_lazy('mmutools:supplier_list'))

    ## ITEM FILE UPLOAD ##


class FileCreateView(MmutoolsEditRequiredMixin, CreateView):
    model = models.File
    template_name = 'mmutools/file_form_popout.html'
    form_class = forms.FileForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"File successfully added for : {my_object}"))
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))

    def get_initial(self):
        item = models.Item.objects.get(pk=self.kwargs['item'])
        return {
            'item': item,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["editable"] = True
        context["item"] = models.Item.objects.get(pk=self.kwargs.get("item"))
        return context


class FileUpdateView(MmutoolsEditRequiredMixin, UpdateView):
    model = models.File
    template_name = 'mmutools/file_form_popout.html'
    form_class = forms.FileForm

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        context["editable"] = True
        return context

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"File record successfully updated for : {my_object}"))
        success_url = reverse_lazy('shared_models:close_me')
        return HttpResponseRedirect(success_url)


class FileDetailView(FileUpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["editable"] = False
        return context

class FileDeleteView(MmutoolsEditRequiredMixin, DeleteView):
    model = models.File
    permission_required = "__all__"
    success_message = 'The file was successfully deleted!'

    def get_template_names(self):
        return "mmutools/generic_confirm_delete_popout.html"

    def delete(self, request, *args, **kwargs):
        my_object = self.get_object()
        my_object.delete()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))


    ## LENDING ##


# class LendingListView(MmutoolsAccessRequired, FilterView):
#     template_name = "mmutools/lending_list.html"
#     filterset_class = filters.LendingFilter
#     queryset = models.Lending.objects.annotate(
#         search_term=Concat('id', 'item', 'quantity_lent', 'lent_to', 'lent_date', output_field=TextField()))
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["my_object"] = models.Lending.objects.first()
#         context["field_list"] = [
#             'id',
#             'item',
#             'quantity_lent',
#             'lent_to',
#             'lent_date',
#
#         ]
#         return context
#
#
# class LendingDetailView(MmutoolsAccessRequired, DetailView):
#     model = models.Lending
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["field_list"] = [
#             'id',
#             'item',
#             'quantity_lent',
#             'lent_to',
#             'lent_date',
#
#         ]
#         return context
#
#
# class LendingUpdateView(MmutoolsEditRequiredMixin, UpdateView):
#     model = models.Lending
#     form_class = forms.LendingForm
#
#     def form_valid(self, form):
#         my_object = form.save()
#         messages.success(self.request, _(f"Lending record successfully updated for : {my_object}"))
#         return super().form_valid(form)
#
#
# class LendingCreateView(MmutoolsEditRequiredMixin, CreateView):
#     model = models.Lending
#     form_class = forms.LendingForm
#
#     def form_valid(self, form):
#         my_object = form.save()
#         messages.success(self.request, _(f"Lending record successfully created for : {my_object}"))
#         return super().form_valid(form)
#
#
# class LendingDeleteView(MmutoolsEditRequiredMixin, DeleteView):
#     model = models.Lending
#     permission_required = "__all__"
#     success_url = reverse_lazy('mmutools:lending_list')
#     success_message = 'The lending agreement was successfully deleted!'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)

    ## INCIDENT ##


class IncidentListView(MmutoolsAccessRequired, FilterView):
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


class IncidentDetailView(MmutoolsAccessRequired, DetailView):
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


class IncidentUpdateView(MmutoolsEditRequiredMixin, UpdateView):
    model = models.Incident
    form_class = forms.IncidentForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Incident record successfully updated for : {my_object}"))
        return super().form_valid(form)


class IncidentCreateView(MmutoolsEditRequiredMixin, CreateView):
    model = models.Incident
    form_class = forms.IncidentForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Incident record successfully created for : {my_object}"))
        return super().form_valid(form)


class IncidentDeleteView(MmutoolsEditRequiredMixin, DeleteView):
    model = models.Incident
    permission_required = "__all__"
    success_url = reverse_lazy('mmutools:incident_list')
    success_message = 'The incident file was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
