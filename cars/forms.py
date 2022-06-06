from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import modelformset_factory
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
            "postal_code",
            "latitude",
            "longitude",
        ]


LocationFormset = modelformset_factory(
    model=models.Location,
    form=LocationForm,
    extra=1,
)

#
# class SpeciesForm(forms.ModelForm):
#     class Meta:
#         model = models.Species
#         fields = "__all__"
#
#
# SpeciesFormset = modelformset_factory(
#     model=models.Species,
#     form=SpeciesForm,
#     extra=1,
# )
#
#
# class RegionForm(forms.ModelForm):
#     class Meta:
#         model = models.Region
#         fields = "__all__"
#
#
# class TransectForm(forms.ModelForm):
#     field_order = ["name"]
#
#     class Meta:
#         model = models.Transect
#         fields = "__all__"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if not kwargs.get("instance"):
#             del self.fields["region"]
#
#
# class SampleForm(forms.ModelForm):
#     class Meta:
#         model = models.Sample
#         fields = "__all__"
#         widgets = {
#             "datetime": forms.DateInput(attrs=dict(type="datetime-local"), format="%Y-%m-%dT%H:%M:%S"),
#             'transect': forms.Select(attrs=chosen_js),
#
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#
# class DiveForm(forms.ModelForm):
#     # field_order = ["name"]
#     class Meta:
#         model = models.Dive
#         fields = "__all__"
#         widgets = {
#             "start_descent": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M:%S"),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # if kwargs.get("instance"):
#         #     self.fields["transect"].queryset = kwargs.get("instance").sample.region.transects.all()
#         # elif kwargs.get("initial"):
#         #     self.fields["transect"].queryset = models.Sample.objects.get(pk=kwargs.get("initial").get("sample")).region.transects.all()
#
#         # self.fields["start_descent"].label += " (yyyy-mm-dd HH:MM:SS)"
#
#     def clean(self):
#         if hasattr(self.instance, "sample"):
#             sample = self.instance.sample
#         else:
#             sample = models.Sample.objects.get(pk=self.initial.get("sample"))
#
#         cleaned_data = super().clean()
#
#         start_descent = cleaned_data.get("start_descent")
#
#         if start_descent and (start_descent.year != sample.datetime.year or
#                               start_descent.month != sample.datetime.month or
#                               start_descent.day != sample.datetime.day):
#             msg = gettext(gettext('This must occur on the same day as the sample: {}').format(date(sample.datetime)))
#             self.add_error('start_descent', msg)
#
#         transect = cleaned_data.get("transect")
#         width_m = cleaned_data.get("width_m")
#         if transect and not width_m:
#             msg = gettext(gettext('If there is a transect associated with this dive, you must provide a width.'))
#             self.add_error('width_m', msg)
#
#
# class SectionForm(forms.ModelForm):
#     class Meta:
#         model = models.Section
#         fields = "__all__"
#         exclude = ["dive"]
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         klass = "form-control form-control-sm"
#
#         self.fields["interval"].widget.attrs = {"v-model": "sectionToEdit.interval", "ref": "top_of_form", "@change": "unsavedSectionWork=true",
#                                                 "class": klass} #":disabled": "sectionToEdit.id",}
#         self.fields["depth_ft"].widget.attrs = {"v-model": "sectionToEdit.depth_ft", "min": 0, "@change": "unsavedSectionWork=true", "step": "0.01",
#                                                 "class": klass}
#         self.fields["percent_sand"].widget.attrs = {"v-model": "sectionToEdit.percent_sand", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
#                                                     "step": "0.01", "class": klass}
#         self.fields["percent_mud"].widget.attrs = {"v-model": "sectionToEdit.percent_mud", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
#                                                    "step": "0.01", "class": klass}
#         self.fields["percent_hard"].widget.attrs = {"v-model": "sectionToEdit.percent_hard", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
#                                                     "step": "0.01", "class": klass}
#         self.fields["percent_algae"].widget.attrs = {"v-model": "sectionToEdit.percent_algae", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
#                                                      "step": "0.01", "class": klass}
#         self.fields["percent_gravel"].widget.attrs = {"v-model": "sectionToEdit.percent_gravel", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
#                                                       "step": "0.01", "class": klass}
#         self.fields["percent_cobble"].widget.attrs = {"v-model": "sectionToEdit.percent_cobble", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
#                                                       "step": "0.01", "class": klass}
#         self.fields["percent_pebble"].widget.attrs = {"v-model": "sectionToEdit.percent_pebble", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
#                                                       "step": "0.01", "class": klass}
#         self.fields["comment"].widget.attrs = {"v-model": "sectionToEdit.comment", "@change": "unsavedSectionWork=true", "row": 3, "class": klass}
#
#
# class ObservationForm(forms.ModelForm):
#     class Meta:
#         model = models.Observation
#         fields = "__all__"
#         exclude = ["section"]
#         widgets = {
#             "comment": forms.TextInput(),
#             "carapace_length_mm": forms.TextInput(),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         klass = "form-control form-control-sm"
#         self.fields["sex"].widget.attrs = {"v-model": "obs.sex", "@change": "updateObservation(obs)", "class": klass}
#         self.fields["egg_status"].widget.attrs = {"v-model": "obs.egg_status", "@change": "updateObservation(obs)", "class": klass, ":disabled": "obs.sex!='f'"}
#         self.fields["carapace_length_mm"].widget.attrs = {"v-model": "obs.carapace_length_mm", "@change": "updateObservation(obs)", "class": klass}
#         self.fields["species"].widget.attrs = {"v-model": "obs.species", "@change": "updateObservation(obs)", "class": klass}
#         self.fields["certainty_rating"].widget.attrs = {"v-model": "obs.certainty_rating", "@change": "updateObservation(obs)", "class": klass}
#         self.fields["comment"].widget.attrs = {"v-model": "obs.comment", "@change": "updateObservation(obs)", "class": klass}
#
#
# class NewObservationForm(forms.ModelForm):
#     class Meta:
#         model = models.Observation
#         fields = "__all__"
#         exclude = ["section"]
#         widgets = {
#             "carapace_length_mm": forms.TextInput(),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         klass = "form-control form-control-sm"
#         self.fields["sex"].widget.attrs = {"v-model": "new_observation.sex", "class": klass,
#                                            "@change": "updateEggStatus(new_observation)"}
#         self.fields["egg_status"].widget.attrs = {"v-model": "new_observation.egg_status", "class": klass}
#         self.fields["carapace_length_mm"].widget.attrs = {"v-model": "new_observation.carapace_length_mm", "class": klass,
#                                                           "@change": "updateLengthCertainty(new_observation)", "ref": "top_of_form1", }
#         self.fields["certainty_rating"].widget.attrs = {"v-model": "new_observation.certainty_rating", "class": klass}
#         self.fields["species"].widget.attrs = {"v-model": "new_observation.species", "class": klass}
#         self.fields["comment"].widget.attrs = {"v-model": "new_observation.comment", "row": 3, "class": klass}
#
#         species_choices = [(obj.id, obj.code_name) for obj in models.Species.objects.all()]
#         species_choices.insert(0, tuple((None, "---")))
#         self.fields["species"].choices = species_choices
#
#
# class ReportSearchForm(forms.Form):
#     REPORT_CHOICES = (
#         (None, "------"),
#         (1, "dive log (xlsx)"),
#         (2, "scuba transect export (csv)"),
#         (6, "outing export (csv)"),
#         (5, "dive export (csv)"),
#         (3, "section export (csv)"),
#         (4, "observation export (csv)"),
#         (None, "------ OPEN DATA STUFF -----"),
#         (7, "Open Data - dataset (csv)"),
#         (8, "Open Data - dictionary (csv)"),
#     )
#     report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
#     year = forms.IntegerField(required=False, label=gettext_lazy('Year'), widget=forms.NumberInput(attrs={"placeholder": "Leave blank for all years"}))
#
#
# class ScubaUserForm(forms.ModelForm):
#     class Meta:
#         model = models.ScubaUser
#         fields = "__all__"
#         widgets = {
#             'user': forms.Select(attrs=chosen_js),
#         }
#
#
# ScubaUserFormset = modelformset_factory(
#     model=models.ScubaUser,
#     form=ScubaUserForm,
#     extra=1,
# )
