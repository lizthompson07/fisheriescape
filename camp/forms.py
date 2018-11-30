from django import forms
from django.core import validators
from . import models


class SiteForm(forms.ModelForm):
    class Meta:
        model = models.Site
        fields = "__all__"

class StationForm(forms.ModelForm):
    class Meta:
        model = models.Station
        fields = "__all__"
        widgets = {
            "latitude_n": forms.NumberInput(attrs={"placeholder":"DD.dddddd",}),
            "longitude_w": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            "description": forms.Textarea(attrs={"rows": "3", }),
            "site": forms.HiddenInput(),
        }


class NoSiteStationForm(forms.ModelForm):
    class Meta:
        model = models.Station
        fields = "__all__"
        widgets = {
            "latitude_n": forms.NumberInput(attrs={"placeholder":"DD.dddddd",}),
            "longitude_w": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            "description": forms.Textarea(attrs={"rows": "3", }),
            # "site": forms.HiddenInput(),
        }


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"

class SearchForm(forms.Form):

    SITE_CHOICES = ((None, "---"),)
    for obj in models.Site.objects.all().order_by("site"):
        SITE_CHOICES = SITE_CHOICES.__add__(((obj.id, obj),))

    STATION_CHOICES = ((None, "---"),)
    for obj in models.Station.objects.all():
        STATION_CHOICES = STATION_CHOICES.__add__(((obj.id, obj),))

    SPECIES_CHOICES = ((None, "---"),)
    for obj in models.Species.objects.all():
        SPECIES_CHOICES = SPECIES_CHOICES.__add__(((obj.id, obj),))


    year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder':"all years"}))
    month = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder':"all months"}))
    site = forms.ChoiceField(required = False, choices=SITE_CHOICES)
    station = forms.ChoiceField(required = False, choices = STATION_CHOICES)
    species = forms.ChoiceField(required = False, choices = SPECIES_CHOICES)

    field_order = ["year","month","site","station","species"]





class SampleForm(forms.ModelForm):
    do_another = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = models.Sample
        exclude = [
            'species',
            'sample_spp',
            'year',
            'month',
            'last_modified',
        ]
        labels={
            'notes':"Misc. notes",
        }

        class_addable = {"class":"addable"}

        widgets = {
            'notes': forms.Textarea(attrs={'rows': '3'}),
            'percent_sand':forms.NumberInput(attrs=class_addable),
            'percent_gravel': forms.NumberInput(attrs=class_addable),
            'percent_rock': forms.NumberInput(attrs=class_addable),
            'percent_mud': forms.NumberInput(attrs=class_addable),
        }

class SampleCreateForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        exclude = [
            'species',
            'sample_spp',
            'year',
            'month',
            'last_modified',
        ]
        labels={
            'notes':"Misc. notes",
        }

        class_addable = {"class": "addable"}

        widgets = {
            'notes': forms.Textarea(attrs={'rows': '3'}),
            'percent_sand': forms.NumberInput(attrs=class_addable),
            'percent_gravel': forms.NumberInput(attrs=class_addable),
            'percent_rock': forms.NumberInput(attrs=class_addable),
            'percent_mud': forms.NumberInput(attrs=class_addable),
        }
class SpeciesObservationForm(forms.ModelForm):

    class Meta:
        model = models.SpeciesObservation
        exclude = ["total",]
        labels={

        }
        widgets = {
            'species':forms.HiddenInput(),
            'sample':forms.HiddenInput(),
            # 'percent_coverage':forms.TextInput(attrs={'placeholder':"Value bewteen 0 and 1"}),
            'notes': forms.Textarea(attrs={"rows":"3"}),

        }



class ReportSearchForm(forms.Form):
    #
    # SITE_CHOICES = ((None, "---"),)
    # for obj in models.Site.objects.all().order_by("site"):
    #     SITE_CHOICES = SITE_CHOICES.__add__(((obj.id, obj),))
    #
    # STATION_CHOICES = ((None, "---"),)
    # for obj in models.Station.objects.all():
    #     STATION_CHOICES = STATION_CHOICES.__add__(((obj.id, obj),))

    SPECIES_CHOICES = ((None, "---"),)
    for obj in models.Species.objects.all():
        SPECIES_CHOICES = SPECIES_CHOICES.__add__(((obj.id, obj),))


    # year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder':"all years"}))
    # month = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder':"all months"}))
    # site = forms.ChoiceField(required = False, choices=SITE_CHOICES)
    # station = forms.ChoiceField(required = False, choices = STATION_CHOICES)
    species = forms.ChoiceField(required = False, choices = SPECIES_CHOICES)

    # field_order = ["year","month","site","station","species"]


# class ProbeMeasurementForm(forms.ModelForm):
#     class Meta:
#         fields = ("__all__")
#         model = models.ProbeMeasurement
#         labels={
#             'time_date':"Date / Time Atlantic Standard Time (yyyy-mm-dd hh:mm:ss)",
#             'probe_depth':"Probe depth (m)",
#             'probe':"Probe name",
#             'temp_c':"Temp (°C)",
#             'sal_ppt':"Salinity (ppt)",
#             'o2_percent':" Disolved oxygen (%)",
#             'o2_mgl':"Disolved oxygen (mg/l)",
#             'sp_cond_ms':"Specific conductance (mS)",
#             'spc_ms':"Conductivity (mS)",
#             'ph':"pH",
#         }
#
#         widgets = {
#             'temp_c':forms.NumberInput(attrs={'placeholder':'°C'}),
#             'time_date':forms.DateTimeInput(attrs={'placeholder':'yyyy-mm-dd hh:mm:ss'}),
#             'sal_ppt':forms.NumberInput(attrs={'placeholder':'ppt'}),
#             'o2_percent':forms.NumberInput(attrs={'placeholder':'%'}),
#             'o2_mgl':forms.NumberInput(attrs={'placeholder':'mg/l'}),
#             'sp_cond_ms':forms.NumberInput(attrs={'placeholder':'mS'}),
#             'spc_ms':forms.NumberInput(attrs={'placeholder':'mS'}),
#             'probe_depth':forms.NumberInput(attrs={'placeholder':'m'}),
#             'last_modified_by':forms.HiddenInput(),
#
#         }
#
# class LineCreateForm(forms.ModelForm):
#     number_plates = forms.IntegerField(label='How many plates on this line?', required=False)
#     number_petris = forms.IntegerField(label='How many petri dishes on this line?', required=False)
#
#     class Meta:
#         model = models.Line
#         fields = "__all__"
#         labels={
#             'collector':"DFO collector tag #",
#             'latitude_n':"Latitude (N)",
#             'longitude_w':"Longitude (W)",
#         }
#         widgets = {
#             'latitude_n':forms.NumberInput(attrs={'placeholder':'decimal degrees'}),
#             'longitude_w':forms.NumberInput(attrs={'placeholder':'decimal degrees'}),
#             'notes':forms.Textarea(attrs={'rows':'5'}),
#             'last_modified_by':forms.HiddenInput(),
#             'sample':forms.HiddenInput(),
#         }
#
# class LineForm(forms.ModelForm):
#     class Meta:
#         model = models.Line
#         fields = "__all__"
#         labels={
#             'collector':"DFO collector tag #",
#             'latitude_n':"Latitude (N)",
#             'longitude_w':"Longitude (W)",
#         }
#         widgets = {
#             'latitude_n':forms.NumberInput(attrs={'placeholder':'decimal degrees'}),
#             'longitude_w':forms.NumberInput(attrs={'placeholder':'decimal degrees'}),
#             'notes':forms.Textarea(attrs={'rows':'5'}),
#             'last_modified_by':forms.HiddenInput(),
#             'sample':forms.HiddenInput(),
#         }
#
# class SurfaceForm(forms.ModelForm):
#     class Meta:
#         model = models.Surface
#         fields = "__all__"
#         exclude = ['species']
#         widgets = {
#             'line':forms.HiddenInput(),
#             'last_modified_by':forms.HiddenInput(),
#         }
#
# class SurfaceImageForm(forms.ModelForm):
#     class Meta:
#         model = models.Surface
#         fields = ('image','last_modified_by')
#         widgets = {
#             'last_modified_by':forms.HiddenInput(),
#         }
#
# class SurfaceSpeciesForm(forms.ModelForm):
#
#     class Meta:
#         model = models.SurfaceSpecies
#         fields = "__all__"
#         labels={
#             'percent_coverage':"Coverage",
#             'longitude_w':"Longitude",
#         }
#         widgets = {
#             'species':forms.HiddenInput(),
#             'surface':forms.HiddenInput(),
#             'percent_coverage':forms.TextInput(attrs={'placeholder':"Value bewteen 0 and 1"}),
#             'last_modified_by':forms.HiddenInput(),
#         }
#
#
# class ReportForm(forms.ModelForm):
#     class Meta:
#         model = models.IncidentalReport
#         exclude = ["season","date_last_modified"]
#
#         labels = {
#             'reporter_name':"Name of person filing report",
#             'notes':"Notes (e.g., habitat, salinity, temperature, etc...) ",
#             'report_date': "Date report received",
#         }
#
#         widgets = {
#             'report_date':forms.DateInput(attrs={'type': 'date'}),
#             'date_of_occurence':forms.DateInput(attrs={'type': 'date'}),
#             'specimens_retained': forms.Select(),
#             'sighting_description': forms.Textarea(attrs={'rows': '3'}),
#             'notes': forms.Textarea(attrs={'rows': '3'}),
#             'last_modified_by':forms.HiddenInput(),
#         }