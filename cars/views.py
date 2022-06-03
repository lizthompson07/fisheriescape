from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy, gettext as _

from cars import models, forms, filters
from cars.mixins import CarsBasicMixin, SuperuserOrAdminRequiredMixin, CarsNationalAdminRequiredMixin, CarsRegionalAdminRequiredMixin, \
    CanModifyVehicleRequiredMixin
from shared_models.views import CommonTemplateView, CommonFormsetView, CommonHardDeleteView, CommonDeleteView, CommonDetailView, CommonUpdateView, \
    CommonFilterView, CommonCreateView


class IndexTemplateView(CarsBasicMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'cars/index.html'


# REFERENCE TABLES #
####################

class CarsUserFormsetView(SuperuserOrAdminRequiredMixin, CommonFormsetView):
    template_name = 'cars/formset.html'
    h1 = "Manage Cars Users"
    queryset = models.CarsUser.objects.all()
    formset_class = forms.CarsUserFormset
    success_url_name = "cars:manage_cars_users"
    delete_url_name = "cars:delete_cars_user"
    container_class = "container bg-light curvy"


class CarsUserHardDeleteView(SuperuserOrAdminRequiredMixin, CommonHardDeleteView):
    model = models.CarsUser
    success_url = reverse_lazy("cars:manage_cars_users")


class VehicleTypeFormsetView(CarsNationalAdminRequiredMixin, CommonFormsetView):
    template_name = 'cars/formset.html'
    h1 = "Manage Vehicle Types"
    queryset = models.VehicleType.objects.all()
    formset_class = forms.VehicleTypeFormset
    success_url_name = "cars:manage_vehicle_types"
    home_url_name = "cars:index"
    delete_url_name = "cars:delete_vehicle_type"


class VehicleTypeHardDeleteView(CarsNationalAdminRequiredMixin, CommonHardDeleteView):
    model = models.VehicleType
    success_url = reverse_lazy("cars:manage_vehicle_types")


class LocationFormsetView(CarsRegionalAdminRequiredMixin, CommonFormsetView):
    template_name = 'cars/formset.html'
    h1 = "Manage Locations"
    queryset = models.Location.objects.all()
    formset_class = forms.LocationFormset
    success_url_name = "cars:manage_locations"
    home_url_name = "cars:index"
    delete_url_name = "cars:delete_location"


class LocationHardDeleteView(CarsRegionalAdminRequiredMixin, CommonHardDeleteView):
    model = models.Location
    success_url = reverse_lazy("cars:manage_locations")


# VEHICLES #
###########

class VehicleListView(CarsBasicMixin, CommonFilterView):
    template_name = 'cars/vehicle_list.html'
    filterset_class = filters.VehicleFilter
    new_object_url = reverse_lazy("cars:vehicle_new")
    row_object_url_name = row_ = "cars:vehicle_detail"
    paginate_by = 10

    def get_queryset(self):
        qp = self.request.GET
        if qp.get("personalized"):
            return self.request.user.vehicles.all()
        return models.Vehicle.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qp = self.request.GET
        if qp.get("personalized"):
            context["personalized"] = True
            context["filter"] = None
            context["paginate_by"] = None
        return context

class VehicleUpdateView(CanModifyVehicleRequiredMixin, CommonUpdateView):
    model = models.Vehicle
    form_class = forms.VehicleForm
    template_name = 'cars/form.html'
    home_url_name = "cars:index"
    parent_crumb = {"title": gettext_lazy("Vehicles"), "url": reverse_lazy("cars:vehicle_list")}
    container_class = "container curvy"
    is_multipart_form_data = True


class VehicleCreateView(CarsBasicMixin, CommonCreateView):
    model = models.Vehicle
    form_class = forms.VehicleForm
    success_url = reverse_lazy('cars:vehicle_list')
    template_name = 'cars/form.html'
    home_url_name = "cars:index"
    parent_crumb = {"title": gettext_lazy("Vehicles"), "url": reverse_lazy("cars:vehicle_list")}
    container_class = "container curvy"
    is_multipart_form_data = True


class VehicleDetailView(CarsBasicMixin, CommonDetailView):
    model = models.Vehicle
    template_name = 'cars/vehicle_detail.html'
    home_url_name = "cars:index"
    parent_crumb = {"title": gettext_lazy("Vehicles"), "url": reverse_lazy("cars:vehicle_list")}
    container_class = "container curvy"
    field_list = [
        "region",
        "location",
        "custodian",
        "vehicle_type",
        "reference_number",
        "make",
        "model",
        "year",
        "max_passengers",
        "is_active",
        "comments",
    ]



class VehicleDeleteView(CanModifyVehicleRequiredMixin, CommonDeleteView):
    model = models.Vehicle
    success_url = reverse_lazy('cars:vehicle_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'cars/confirm_delete.html'
    container_class = "container curvy"
