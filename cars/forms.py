from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import modelformset_factory
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy, gettext

from shared_models.models import Section
from . import models
from .utils import is_dt_intersection

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
            "custodian": forms.Select(attrs=chosen_js),
            "section": forms.Select(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        section_choices = [(s.id, s.full_name) for s in Section.objects.all().order_by("division__branch__region", "division__branch", "division", "name")]
        section_choices.insert(0, (None, "-----"))
        self.fields['section'].choices = section_choices


class ReservationForm(forms.ModelForm):
    box1 = forms.BooleanField(required=True)
    box2 = forms.BooleanField(required=True)
    box3 = forms.BooleanField(required=True)

    # field_order = [
    #     "date_range",
    # ]
    # date_range = forms.CharField(widget=forms.TextInput(attrs=attr_fp_date_range),
    #                              label=gettext_lazy("What dates are you looking for?"), required=True)

    class Meta:
        model = models.Reservation
        # exclude = ["start_date", "end_date"]
        fields = "__all__"
        widgets = {
            "vehicle": forms.Select(attrs=chosen_js),
            "primary_driver": forms.Select(attrs=chosen_js),
            "other_drivers": forms.SelectMultiple(attrs=chosen_js),
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
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
            self.fields["box1"].label = mark_safe(
                gettext(
                    "I have signed the <a target='_blank' href='{url}'>Acknowledgement of Motor Vehicle Operator Role and Responsibilities Form</a>.").format(
                    url="https://forms-formulaires.dfo-mpo.gc.ca/Forms/FP_0024-E.pdf"))
            self.fields["box2"].label = mark_safe(
                gettext("I have signed off on the safe work procedure <a target='_blank' href='{url}'>Driving a Road Vehicle</a>.").format(
                    url=static("cars/SWP 09.pdf")))
            self.fields["box3"].label = gettext("I have my manager's authorization to proceed.")

    def clean_primary_driver(self):
        primary_driver = self.cleaned_data['primary_driver']
        if not primary_driver:
            raise forms.ValidationError(gettext("You must select a primary driver!"))
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

        start_date = cleaned_data["start_date"]
        end_date = cleaned_data["end_date"]

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
                                      label=gettext_lazy("Pick-up location"), help_text=gettext_lazy("leave blank for all"))
    vehicle_type = forms.ModelChoiceField(required=False,
                                          queryset=models.VehicleType.objects.filter(vehicles__isnull=False).distinct(),
                                          label=gettext_lazy("Vehicle type"), help_text=gettext_lazy("leave blank for all"))
    vehicle_section = forms.ModelChoiceField(required=False,
                                             queryset=models.Section.objects.filter(vehicles__isnull=False).distinct(), widget=forms.Select(attrs=chosen_js),
                                             label=gettext_lazy("DFO Section"), help_text=gettext_lazy("leave blank for all"))
    vehicle = forms.ModelChoiceField(required=False, queryset=models.Vehicle.objects.all(), widget=forms.Select(attrs=chosen_js),
                                     label=gettext_lazy("Vehicle"), help_text=gettext_lazy("leave blank for all"))
    no_passengers = forms.IntegerField(required=False, label=gettext_lazy("Passenger minimum capacity"), help_text=gettext_lazy("leave blank for all"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        section_choices = [(s.id, s.full_name) for s in Section.objects.filter(vehicles__isnull=False).distinct().order_by(
            "division__branch__region", "division__branch", "division", "name")]
        section_choices.insert(0, (None, "-----"))
        self.fields['vehicle_section'].choices = section_choices


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


class VehicleShortForm(VehicleForm):
    class Meta:
        model = models.Vehicle
        exclude = [
            "thumbnail",
        ]
        widgets = {
            "make": forms.Textarea(),
            "model": forms.Textarea(),
            "section": forms.Select(attrs=chosen_js),
        }


VehicleFormset = modelformset_factory(
    model=models.Vehicle,
    form=VehicleShortForm,
    extra=1,
)


class FAQForm(forms.ModelForm):
    class Meta:
        model = models.FAQ
        fields = "__all__"


FAQFormset = modelformset_factory(
    model=models.FAQ,
    form=FAQForm,
    extra=1,
)


class ReferenceMaterialForm(forms.ModelForm):
    class Meta:
        model = models.ReferenceMaterial
        fields = "__all__"
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"})
        }


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = (
        (None, "---"),
        (1, "Species counts by year"),
        (3, "Annual watershed report (PDF)"),
        (4, "Annual watershed spreadsheet (XLSX)"),
        (6, "AIS export (CSV)"),
        (8, "OPEN DATA: web map services report ENGLISH (CSV)"),
        (13, "OPEN DATA: web map services report FRENCH (CSV)"),
        (11, "OPEN DATA: species list (CSV)"),
        (7, "OPEN DATA: data dictionary (CSV)"),
        (5, "OPEN DATA - Version 1: Species observations (CSV)"),
        (9, "OPEN DATA - Version 2: Summary by station by year (CSV)"),
        (12, "OPEN DATA - Version 3: CAMP samples (CSV)"),
    )

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    species = forms.MultipleChoiceField(required=False)
    ais_species = forms.MultipleChoiceField(required=False, label="AIS species")
    year = forms.CharField(required=False, widget=forms.NumberInput())
    site = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        SITE_CHOICES = [(obj.id, str(obj)) for obj in models.Site.objects.all()]
        SITE_CHOICES.insert(0, tuple((None, "All Sites")))

        SPECIES_CHOICES = [(obj.id, str(obj)) for obj in models.Species.objects.all().order_by("common_name_eng")]
        SPECIES_CHOICES.insert(0, tuple((None, "-------")))

        AIS_CHOICES = [(obj.id, "{} - {}".format(obj.common_name_eng, obj.scientific_name)) for obj in
                       models.Species.objects.filter(ais=True).order_by("common_name_eng")]

        self.fields['site'].choices = SITE_CHOICES
        self.fields['species'].choices = SPECIES_CHOICES
        self.fields['ais_species'].choices = AIS_CHOICES

        # SPECIES_CHOICES = ((None, "---"),)
        # for obj in models.Species.objects.all().order_by("common_name_eng"):
        #     SPECIES_CHOICES = SPECIES_CHOICES.__add__(((obj.id, obj),))
        #
        # SITE_CHOICES = ((None, "All Stations"),)
        # for obj in models.Site.objects.all():
        #     SITE_CHOICES = SITE_CHOICES.__add__(((obj.id, obj),))
