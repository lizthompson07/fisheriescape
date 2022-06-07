from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import modelformset_factory
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy, gettext

from . import models
from .utils import is_dt_intersection, get_dates_from_range

attr_fp_date_time = {"class": "fp-date-time-with-seconds", "placeholder": "Select Date and Time.."}
attr_fp_date_range = {"class": "fp-date-range", "placeholder": gettext_lazy("Click to select a range of dates..")}

chosen_js = {"class": "chosen-select-contains"}
YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class VehicleForm(forms.ModelForm):
    class Meta:
        model = models.Vehicle
        fields = "__all__"
        widgets = {
            "custodian": forms.Select(attrs=chosen_js)
        }


class ReservationForm(forms.ModelForm):
    box1 = forms.BooleanField(required=True)
    box2 = forms.BooleanField(required=True)
    box3 = forms.BooleanField(required=True)

    field_order = [
        "date_range",
    ]
    date_range = forms.CharField(widget=forms.TextInput(attrs=attr_fp_date_range),
                                 label=gettext_lazy("What dates are you looking for?"), required=True)

    class Meta:
        model = models.Reservation
        exclude = ["start_date", "end_date"]

        widgets = {
            "vehicle": forms.Select(attrs=chosen_js),
            "primary_driver": forms.Select(attrs=chosen_js),
            "other_drivers": forms.SelectMultiple(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        user_qs = User.objects.filter(is_active=True).order_by("first_name", "last_name")
        self.fields["primary_driver"].queryset = user_qs
        self.fields["other_drivers"].queryset = user_qs
        if kwargs.get("instance"):
            del self.fields["box1"]
            del self.fields["box2"]
            del self.fields["box3"]
        else:
            self.fields["box1"].label = mark_safe("I have signed the <a href='https://forms-formulaires.dfo-mpo.gc.ca/Forms/FP_0024-E.pdf'>Acknowledgement of Motor Vehicle Operator Role and Responsibilities Form</a>.")
            self.fields["box2"].label = mark_safe("I have signed off on the safe work procedure <a href='#'>Driving a Road Vehicle</a>.")
            self.fields["box3"].label = "I have my manager's authorization to proceed."

    def clean_primary_driver(self):
        primary_driver = self.cleaned_data['primary_driver']
        if not primary_driver:
            raise forms.ValidationError("You must select a primary driver!")
        return primary_driver

    def clean(self):
        cleaned_data = super().clean()
        if not self.is_valid():
            return cleaned_data
        # make sure there is no intersection with another APPROVED reservation
        vehicle = cleaned_data["vehicle"]

        # in the more simple scenario, this is a new request
        if not self.instance.id:
            approved_reservations = vehicle.reservations.filter(status=10)
        # otherwise we need to exclude the request we are currently looking at
        else:
            approved_reservations = vehicle.reservations.filter(status=10).filter(~Q(id=self.instance.id))

        dates = get_dates_from_range(cleaned_data["date_range"])
        start_date = dates[0]
        end_date = dates[1]

        for r in approved_reservations:
            if is_dt_intersection(r.start_date, r.end_date, start_date, end_date):
                error_msg = gettext("Sorry, the time requested overlaps with another approved reservation.")
                raise forms.ValidationError(error_msg)

        return self.cleaned_data


class VehicleFinderForm(forms.Form):
    date_range = forms.CharField(widget=forms.TextInput(attrs=attr_fp_date_range),
                                 label=gettext_lazy("What dates are you looking for?"), required=True)
    # region = forms.ModelChoiceField(required=False, queryset=Region.objects.filter(vehicles__isnull=False).distinct(), label=gettext_lazy("Region"))
    location = forms.ModelChoiceField(required=False,
                                      queryset=models.Location.objects.filter(vehicles__isnull=False).distinct(),
                                      label=gettext_lazy("Pick-up location"))
    vehicle_type = forms.ModelChoiceField(required=False,
                                          queryset=models.VehicleType.objects.filter(vehicles__isnull=False).distinct(),
                                          label=gettext_lazy("Vehicle type"))
    vehicle = forms.ModelChoiceField(required=False, queryset=models.Vehicle.objects.all(),
                                     label=gettext_lazy("Vehicle"))
    no_passengers = forms.IntegerField(required=False, label=gettext_lazy("Passenger minimum capacity"))


class CarsUserForm(forms.ModelForm):
    class Meta:
        model = models.CarsUser
        fields = "__all__"
        widgets = {
            'user': forms.Select(attrs=chosen_js),
        }


CarsUserFormset = modelformset_factory(
    model=models.CarsUser,
    form=CarsUserForm,
    extra=1,
)


class VehicleTypeForm(forms.ModelForm):
    class Meta:
        model = models.VehicleType
        fields = "__all__"


VehicleTypeFormset = modelformset_factory(
    model=models.VehicleType,
    form=VehicleTypeForm,
    extra=1,
)


class LocationForm(forms.ModelForm):
    class Meta:
        model = models.Location
        fields = [
            "region",
            "name",
            "nom",
            "address",
            "city",
            "province",
            "postal_code",
            "latitude",
            "longitude",
        ]


LocationFormset = modelformset_factory(
    model=models.Location,
    form=LocationForm,
    extra=1,
)


class VehicleShortForm(forms.ModelForm):
    class Meta:
        model = models.Vehicle
        exclude = [
            "thumbnail",
        ]


VehicleFormset = modelformset_factory(
    model=models.Vehicle,
    form=VehicleShortForm,
    extra=1,
)
