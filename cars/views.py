from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy, gettext as _

from cars import models, forms, filters, emails
from cars.mixins import CarsBasicMixin, SuperuserOrAdminRequiredMixin, CarsNationalAdminRequiredMixin, CarsRegionalAdminRequiredMixin, \
    CanModifyVehicleRequiredMixin, CanModifyReservationRequiredMixin, CarsAdminRequiredMixin
from cars.utils import get_dates_from_range, is_dt_intersection
from dm_apps.utils import custom_send_mail
from lib.functions.custom_functions import listrify
from shared_models.views import CommonTemplateView, CommonFormsetView, CommonHardDeleteView, CommonDeleteView, CommonDetailView, CommonUpdateView, \
    CommonFilterView, CommonCreateView, CommonFormView


class IndexTemplateView(CarsBasicMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'cars/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["requests_waiting"] = models.Reservation.objects.filter(vehicle__custodian=self.request.user, status=1).count()
        return context

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


class LocationFormsetView(CarsAdminRequiredMixin, CommonFormsetView):
    template_name = 'cars/formset.html'
    h1 = "Manage Locations"
    queryset = models.Location.objects.all()
    formset_class = forms.LocationFormset
    success_url_name = "cars:manage_locations"
    home_url_name = "cars:index"
    delete_url_name = "cars:delete_location"


class LocationHardDeleteView(CarsAdminRequiredMixin, CommonHardDeleteView):
    model = models.Location
    success_url = reverse_lazy("cars:manage_locations")


class VehicleFinder(CarsBasicMixin, CommonFormView):
    template_name = 'cars/vehicle_finder.html'
    form_class = forms.VehicleFinderForm
    h1 = gettext_lazy("Find a Vehicle")

    def get_initial(self):
        qp = self.request.GET
        payload = dict()
        if qp.get("start_date") and qp.get("end_date"):
            payload["date_range"] = f"{qp.get('start_date')} to {qp.get('end_date')}"
        if qp.get("vehicle_type"):
            payload["vehicle_type"] = qp.get('vehicle_type')
        if qp.get("max_passengers__gte"):
            payload["no_passengers"] = qp.get('max_passengers__gte')
        if qp.get("location"):
            payload["location"] = qp.get('location')
        if qp.get("id"):
            payload["vehicle"] = qp.get('id')
        return payload





    def form_valid(self, form):

        # let's see what we got
        date_range = form.cleaned_data["date_range"]
        # region = form.cleaned_data["region"]
        location = form.cleaned_data["location"]
        vehicle_type = form.cleaned_data["vehicle_type"]
        vehicle = form.cleaned_data["vehicle"]
        no_passengers = form.cleaned_data["no_passengers"]

        dates = get_dates_from_range(date_range)
        start_date = dates[0]
        end_date = dates[1]
        query_string = f"?start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}&"

        if location:
            query_string += f"location={location.id}&"
        if vehicle_type:
            query_string += f"vehicle_type={vehicle_type.id}&"
        if vehicle:
            query_string += f"id={vehicle.id}&"
        if no_passengers:
            query_string += f"max_passengers__gte={no_passengers}&"

        good_vehicles = [v.id for v in models.Vehicle.objects.all()]
        for r in models.Reservation.objects.filter(status=10, is_complete=False):
            if is_dt_intersection(r.start_date, r.end_date, start_date, end_date):
                # then we have to remove the vehicle
                try:
                    good_vehicles.remove(r.vehicle_id)
                except ValueError:
                    pass
        query_string += f"ids={listrify(good_vehicles, separator=',')}&"

        return HttpResponseRedirect(reverse("cars:vehicle_list") + query_string)


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
        elif qp.get("ids"):
            if qp.get("ids") == "None":
                ids = []
            else:
                ids = qp.get("ids").split(",")
            return models.Vehicle.objects.filter(id__in=ids)
        else:
            return models.Vehicle.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qp = self.request.GET
        if qp.get("personalized"):
            context["personalized"] = True
            context["filter"] = None
            context["paginate_by"] = None
        if qp.get("ids"):
            context["h1"] = _("Your Search Results")
            context["filter"] = None
            context["paginate_by"] = None
            context["new_object_button"] = None
        return context


class VehicleUpdateView(CanModifyVehicleRequiredMixin, CommonUpdateView):
    model = models.Vehicle
    form_class = forms.VehicleForm
    template_name = 'cars/form.html'
    home_url_name = "cars:index"
    grandparent_crumb = {"title": gettext_lazy("Vehicles"), "url": reverse_lazy("cars:vehicle_list")}
    is_multipart_form_data = True

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cars:vehicle_detail", args=[self.get_object().id])}


class VehicleCreateView(CarsBasicMixin, CommonCreateView):
    model = models.Vehicle
    form_class = forms.VehicleForm
    success_url = reverse_lazy('cars:vehicle_list')
    template_name = 'cars/form.html'
    home_url_name = "cars:index"
    parent_crumb = {"title": gettext_lazy("Vehicles"), "url": reverse_lazy("cars:vehicle_list")}
    is_multipart_form_data = True

    def get_initial(self):
        return dict(custodian=self.request.user)


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
    delete_protection = False
    grandparent_crumb = {"title": gettext_lazy("Vehicles"), "url": reverse_lazy("cars:vehicle_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cars:vehicle_detail", args=[self.get_object().id])}


# RESERVATIONS #
################

class ReservationListView(CarsBasicMixin, CommonFilterView):
    template_name = 'cars/list.html'
    filterset_class = filters.ReservationFilter
    # new_object_url = reverse_lazy("cars:rsvp_new")
    row_object_url_name = row_ = "cars:rsvp_detail"
    paginate_by = 10
    field_list = [
        {"name": 'status', "class": "", "width": ""},
        {"name": 'start_date', "class": "", "width": ""},
        {"name": 'end_date', "class": "", "width": ""},
        {"name": 'destination', "class": "", "width": ""},
        {"name": 'vehicle', "class": "", "width": ""},
        {"name": 'primary_driver', "class": "", "width": ""},
        {"name": 'other_drivers', "class": "", "width": ""},
    ]

    def get_queryset(self):
        qp = self.request.GET
        if qp.get("personalized"):
            return self.request.user.vehicle_reservations.all()
        elif qp.get("my_vehicles"):
            return models.Reservation.objects.filter(vehicle__custodian=self.request.user).order_by("status")
        return models.Reservation.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qp = self.request.GET
        if qp.get("personalized"):
            context["personalized"] = True
            context["filter"] = None
            context["paginate_by"] = None
        return context


class ReservationUpdateView(CanModifyReservationRequiredMixin, CommonUpdateView):
    model = models.Reservation
    form_class = forms.ReservationForm
    template_name = 'cars/form.html'
    home_url_name = "cars:index"
    # grandparent_crumb = {"title": gettext_lazy("Reservations"), "url": reverse_lazy("cars:rsvp_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cars:rsvp_detail", args=[self.get_object().id])}

    def get_initial(self):
        payload = dict()
        obj = self.get_object()
        if obj.start_date:
            payload["date_range"] = f"{obj.start_date.strftime('%Y-%m-%d')} to {obj.end_date.strftime('%Y-%m-%d')}"
        return payload

    def form_valid(self, form):
        obj = form.save(commit=False)
        date_range = form.cleaned_data["date_range"]
        if date_range:
            dates = get_dates_from_range(date_range)
            obj.start_date = dates[0]
            obj.end_date = dates[1]
        obj.updated_by = self.request.user
        return super().form_valid(form)


class ReservationCreateView(CarsBasicMixin, CommonCreateView):
    model = models.Reservation
    form_class = forms.ReservationForm
    success_url = reverse_lazy('cars:rsvp_list')
    template_name = 'cars/form.html'
    home_url_name = "cars:index"
    # parent_crumb = {"title": gettext_lazy("Reservations"), "url": reverse_lazy("cars:rsvp_list")}

    def get_initial(self):
        qp = self.request.GET
        payload = dict(primary_driver=self.request.user)
        if qp.get("start_date") and qp.get("end_date"):
            payload["date_range"] = f"{qp.get('start_date')} to {qp.get('end_date')}"
        if qp.get("vehicle"):
            payload["vehicle"] = qp.get('vehicle')
        return payload

    def form_valid(self, form):
        obj = form.save(commit=False)
        date_range = form.cleaned_data["date_range"]
        if date_range:
            dates = get_dates_from_range(date_range)
            obj.start_date = dates[0]
            obj.end_date = dates[1]
        obj.created_by = self.request.user
        obj = form.save(commit=True)
        email = emails.RSVPEmail(self.request, obj)
        # send the email object
        email.send()
        return super().form_valid(form)


class ReservationDetailView(CarsBasicMixin, CommonDetailView):
    model = models.Reservation
    template_name = 'cars/rsvp_detail.html'
    home_url_name = "cars:index"
    # parent_crumb = {"title": gettext_lazy("Reservations"), "url": reverse_lazy("cars:rsvp_list")}
    field_list = [
        "status",
        "vehicle",
        "vehicle.custodian|{}".format(_("custodian")),
        "destination",
        "primary_driver",
        "start_date",
        "end_date",
        "other_drivers",
        "comments",

    ]


class ReservationDeleteView(CanModifyReservationRequiredMixin, CommonDeleteView):
    model = models.Reservation
    success_url = reverse_lazy('cars:rsvp_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'cars/confirm_delete.html'
    # grandparent_crumb = {"title": gettext_lazy("Reservations"), "url": reverse_lazy("cars:rsvp_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cars:rsvp_detail", args=[self.get_object().id])}


def rsvp_action(request, pk, action):
    rsvp = get_object_or_404(models.Reservation, pk=pk)
    if action == "accept":
        rsvp.status = 10
        rsvp.save()
        email = emails.ApprovedEmail(request, rsvp)
        email.send()
    elif action == "deny":
        rsvp.status = 20
        rsvp.save()
        email = emails.DeniedEmail(request, rsvp)
        email.send()
    elif action == "reset":
        rsvp.status = 1
        rsvp.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
