from _ast import mod

from bokeh.core.property.dataspec import field
from django import forms
from whalesdb import models
from django.utils.translation import gettext_lazy as _
from django.forms.models import inlineformset_factory


def get_short_labels(for_model):

    # You can override the longer more descriptive labels from get_descriptions()
    # here. If not overriden the else clause will just call get_descriptions()

    if for_model is models.EqhHydrophoneProperties:
        labels = {
            'emm': _("Make & Model"),
            'eqh_range_min': _("Bottom frequency"),
            'eqh_range_max': _("Top frequency"),
        }
    elif for_model is models.EcpChannelProperties:
        labels = {
            'ecp_channel_no': _("Channel number"),
            'eqa_adc_bits': _("ADC Bits"),
            'ecp_voltage_range_min': _("Voltage Range Minimum"),
            'ecp_voltage_range_max': _("Voltage Range Maximum"),
            'ecp_gain': _("Gain in dB."),
        }
    elif for_model is models.EprEquipmentParameters:
        labels = {
            'prm': _("Equipment Parameters"),
        }
    elif for_model is models.RscRecordingSchedules:
        labels = {
            'rsc_name': _("Schedule Name"),
            'rsc_period': _("Period"),
        }
    elif for_model is models.StnStations:
        labels = {
            'stn_name': _('Name'),
            'stn_code': _('Code'),
            'stn_revision': _('Revision'),
            'stn_planned_lat': _('Latitude'),
            'stn_planned_lon': _('Longitude'),
            'stn_planned_depth': _('Depth (meters)'),
            'stn_notes': _('Notes'),
        }
    else:
        labels = get_descriptions(for_model)

    return labels


def get_descriptions(for_model):
    labels = {}
    if for_model is models.CrsCruises:
        labels = {
            'crs_name': _('Cruise Name'),
            'crs_pi_name': _('Principal Investigator Name'),
            'crs_institute_name': _('Institute Name'),
            'crs_geographic_location': _('Geographic Location'),
            'crs_start_date': _('Start Date'),
            'crs_end_date': _('End Date'),
            'crs_notes': _('Cruise Notes'),
        }
    elif for_model is models.DepDeployments:
        labels = {
            'dep_year': _('Deployment Year'),
            'dep_month': _('Deployment Month'),
            'stn': _('Station'),
            'dep_name': _('Deployment Name'),
            'prj': _('Project'),
            'mor': _('Mooring Setup'),
        }
    elif for_model is models.EdaEquipmentAttachments:
        labels = {
            "eqp": _("Equipment"),
            "dep": _("Deployment"),
            "rec": _("Recording Event"),
        }
    elif for_model is models.EcpChannelProperties:
        labels = {
            'ecp_channel_no': _("Channel number"),
            'eqa_adc_bits': _("ADC Bits represented in this channel"),
            'ecp_voltage_range_min': _("Voltage Range Minimum"),
            'ecp_voltage_range_max': _("Voltage Range Maximum"),
            'ecp_gain': _("How much a channel is amplified in dB."),
        }
    elif for_model is models.EhaHydrophoneAttachements:
        labels = {
            "eda": _("Equipment Attached To"),
            "eqp": _("Hydrophone"),
        }
    elif for_model is models.EmmMakeModel:
        labels = {
            'eqt': _("Equipment category"),
            'emm_make': _("Equipment make"),
            'emm_model': _("Equipment model"),
            'emm_depth_rating': _("The depth in metres this piece of equipment is rated for"),
            'emm_description': _("Short description of the piece of equipment"),
        }
    elif for_model is models.EqaAdcBitsCode:
        labels = {
            'eqa_id': _('Code ID'),
            'eqa_name': _('Code Value'),
        }
    elif for_model is models.EprEquipmentParameters:
        labels = {
            'prm': _("The parameter type attached to a piece of equipment"),
        }
    elif for_model is models.EqhHydrophoneProperties:
        labels = {
            'eqh_range_min': _("Bottom frequency in the functional flat range of the hydrophone in Hz (+-3 dB unless "
                               "stated in notes)"),
            'eqh_range_max': _("Top frequency in the functional flat range of the hydrophone in Hz (+-3 dB unless "
                               "stated in notes)"),
        }
    elif for_model is models.EqpEquipment:
        labels = {
            'emm': _("Make and Model"),
            'eqp_serial': _("Serial Number"),
            'eqp_asset_id': _("Asset ID"),
            'eqp_date_purchase': _("Date Purchased"),
            'eqp_notes': _("Notes"),
        }
    elif for_model is models.EqtEquipmentTypeCode:
        labels = {
            'eqt_id': _("Equipment Type Code ID"),
            'eqt_name': _("Equipment Type Code Name"),
        }
    elif for_model is models.MorMooringSetups:
        labels = {
            'mor_name': _('Mooring Setup Name'),
            'mor_max_depth': _('Max Depth'),
            'mor_link_setup_image': _('Setup Image Location'),
            'mor_additional_equipment': _('Additional Equipment'),
            'mor_general_moor_description': _('General Description'),
            'more_notes': _('Notes'),
        }
    elif for_model is models.PrmParameterCode:
        labels = {
            'prm_id': _('Parameter ID'),
            'prm_name': _('Parameter Name'),
        }
    elif for_model is models.PrjProjects:
        labels = {
            'prj_name': _('Project Name'),
            'prj_descrption': _('Project Description'),
            'prj_url': _('Project URL'),
        }
    elif for_model is models.RecRecordingEvents:
        labels = {
            'rsc': _("Recording schedule associated with this recording event"),
            'tea_id_setup_by': _("Team member who programmed the recording setup"),
            'rec_date_of_system_chk': _("Recording date of the system check (Time in UTC)"),
            'tea_id_checked_by': _("Team member who prefored the System Check"),
            'rec_date_first_recording': _("Date of first recording when the equipment is turned on for deployment."),
            'rec_date_last_recording': _("Date of last recording"),
            'rec_total_memory_used': _("Total memory used for number of recorded files"),
            'rec_hf_mem': _("High Frequency Memory usage in Gigabytes (GB)"),
            'rec_lf_mem': _("Low Frequency Memory usage in Gigabytes (GB)"),
            'rec_date_data_download': _("Date the data has been downloaded from equipment"),
            'rec_data_store_url': _("URL of the location the data storage"),
            'tea_id_downloaded_by': _("Team member who backed up the data"),
            'rec_date_data_backed_up': _("Date data was backed up"),
            'rec_data_backup_url': _("URL of the data backup location"),
            'tea_id_backed_up_by': _("Team member who backed up the data"),
            'rec_channel_count': _("The number of channels used to record data, one recording per channel"),
            'rec_notes': _("Comments on the recording and data"),
            'rtt': _("Time zone data files use. Should be UTC, but occasionally for legacy data  will be in some "
                     "local format."),
            'rec_first_in_water': _("First in water recording"),
            'rec_last_in_water': _("Last in water recording"),
        }
    elif for_model is models.RscRecordingSchedules:
        labels = {
            'rsc_name': _("A human readable name for this duty cycle if it is to be used as a preset configuration"),
            'rsc_period': _("Unit of time before the recording schedul repeats (seconds)"),
        }
    elif for_model is models.RstRecordingStage:
        labels = {
            'rst_channel_no': _("Channel Number this stage is being recorded on"),
            'rsc': _("The recording schedule this stage belongs to"),
            'rst_active': _("(A)ctive or (S)leep"),
            'rst_duration': _("The number of seconds this stage is active fore"),
            'rst_rate': _("Sampling rate in Hertz (Hz)"),
            'rst_gain': _("Decibles (dB)"),
        }
    elif for_model is models.RttTimezoneCode:
        labels = {
            'rtt_id': _("Time Zone ID"),
            'rtt_abb': _('Time Zone Abbreviation'),
            'rtt_name': _('Time Zone Name'),
            'rtt_offset': _('Time Zone Offset'),
        }
    elif for_model is models.SetStationEventCode:
        labels = {
            'set_id': _('Station Event Code ID'),
            'set_name': _('Station Event Code Name'),
            'set_description': _('Station Event Code Description'),
        }
    elif for_model is models.SteStationEvents:
        labels = {
            'dep': _('Deployment'),
            'set_type': _('Event Type'),
            'ste_date': _('Event Date'),
            'crs': _('Cruise'),
            'ste_lat_ship': _('Latitude, by ship instruments'),
            'ste_lon_ship': _('Longitude, by ship instruments'),
            'ste_depth_ship': _('Depth, by ship instruments'),
            'ste_lat_mcal': _('Latitude, MCAL'),
            'ste_lon_mcal': _('Longitude, MCAL'),
            'ste_depth_mcal': _('Depth, MCAL'),
            'ste_team': _('Team'),
            'ste_instrument_cond': _('Instrument Conditions'),
            'ste_weather_cond': _('Weather Conditions'),
            'ste_logs': _('Event Log Location'),
            'ste_notes': _('Event Notes'),
        }
    elif for_model is models.StnStations:
        labels = {
            'stn_name': _('Station Name'),
            'stn_code': _('Code or abbreviation used for a station'),
            'stn_revision': _('Station Revision'),
            'stn_planned_lat': _('Planned Latitude'),
            'stn_planned_lon': _('Planned Longitude'),
            'stn_planned_depth': _('Planned Depth'),
            'stn_notes': _('Station Notes'),
        }
    elif for_model is models.TeaTeamMembers:
        labels = {
            'tea_abb': _("Short Name of the team member"),
            'tea_last_name': _("Last Name of the team member"),
            'tea_first_name': _("First Name of the team Member"),
        }
    else:
        print('No descriptions found for object ' + str(type(for_model)) + "'")

    return labels


class CrsForm(forms.ModelForm):

    class Meta:
        model = models.CrsCruises
        labels = get_descriptions(model)
        fields = labels.keys()
        widgets = {
            'crs_notes': forms.Textarea(attrs={"rows": 2}),
            'crs_start_date': forms.DateInput(attrs={"type": "date"}),
            'crs_end_date': forms.DateInput(attrs={"type": "date"}),
        }


class DepForm(forms.ModelForm):

    class Meta:
        model = models.DepDeployments
        labels = get_descriptions(model)
        fields = labels.keys()


class EdaForm(forms.ModelForm):

    class Meta:
        model = models.EdaEquipmentAttachments
        labels = get_descriptions(model)
        fields = labels.keys()


class EdhForm(forms.ModelForm):

    class Meta:
        model = models.EhaHydrophoneAttachements
        labels = get_descriptions(model)
        fields = labels.keys()


class EcpChannelPropertiesForm(forms.ModelForm):

    def get_initial_for_field(self, field, field_name):
        if field_name is 'ecp_channel_no':
            return 1

        return super().get_initial_for_field(field, field_name)

    class Meta:
        model = models.EcpChannelProperties
        labels = get_descriptions(model)
        fields = labels.keys()


class EprForm(forms.ModelForm):

    class Meta:
        model = models.EprEquipmentParameters
        labels = get_descriptions(model)
        fields = labels.keys()


class EqaForm(forms.ModelForm):

    class Meta:
        model = models.EqaAdcBitsCode
        labels = get_descriptions(model)
        fields = labels.keys()
        widgets = {
            'eqa_id': forms.HiddenInput()
        }


class EmmForm(forms.ModelForm):

    eqt = forms.ChoiceField(label=_("Equipment category"))
    emm_make = forms.CharField(max_length=50, label=_("Equipment make"))
    emm_model = forms.CharField(max_length=50, label=_("Equipment model"))
    emm_depth_rating = forms.IntegerField(label=_("The depth in metres this piece of equipment is rated for"))
    emm_description = forms.CharField(max_length=500, label=_("Short description of the piece of equipment"))

    class Meta:
        model = models.EmmMakeModel

        labels = get_descriptions(model)
        fields = list(labels.keys())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        eqt_choices = models.EqtEquipmentTypeCode.objects.all().values_list()
        self.fields['eqt'].choices = eqt_choices


class EqrForm(EmmForm):

    class Meta:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['eqt'].initial = 1


class EqhForm(forms.ModelForm):

    eqt = forms.ChoiceField(label=_("Equipment category"))
    emm_make = forms.CharField(max_length=50, label=_("Equipment make"))
    emm_model = forms.CharField(max_length=50, label=_("Equipment model"))
    emm_depth_rating = forms.IntegerField(label=_("The depth in metres this piece of equipment is rated for"))
    emm_description = forms.CharField(max_length=500, label=_("Short description of the piece of equipment"))

    class Meta:
        model = models.EqhHydrophoneProperties

        p_lbls = get_descriptions(models.EmmMakeModel)
        fields = list(p_lbls.keys())

        labels = get_descriptions(model)
        fields.extend(list(labels.keys()))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        eqt_choices = models.EqtEquipmentTypeCode.objects.all().values_list()
        self.fields['eqt'].choices = eqt_choices
        self.fields['eqt'].initial = 2


class EqpForm(forms.ModelForm):

    class Meta:
        model = models.EqpEquipment
        labels = get_descriptions(model)
        fields = labels.keys()

        widgets = {
            'eqp_notes': forms.Textarea(attrs={"rows": 2}),
            'eqp_date_purchase': forms.DateInput(attrs={"type": "date"}),
        }


class EqrForm(forms.ModelForm):
    eqt = forms.ChoiceField(label=_("Equipment category"))
    emm_make = forms.CharField(max_length=50, label=_("Equipment make"))
    emm_model = forms.CharField(max_length=50, label=_("Equipment model"))
    emm_depth_rating = forms.IntegerField(label=_("The depth in metres this piece of equipment is rated for"))
    emm_description = forms.CharField(max_length=500, label=_("Short description of the piece of equipment"))

    class Meta:
        model = models.EmmMakeModel

        p_lbls = get_descriptions(models.EmmMakeModel)
        fields = list(p_lbls.keys())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        eqt_choices = models.EqtEquipmentTypeCode.objects.all().values_list()
        self.fields['eqt'].choices = eqt_choices


class EqtForm(forms.ModelForm):

    class Meta:
        model = models.EqtEquipmentTypeCode
        labels = get_descriptions(model)
        fields = labels.keys()
        widgets = {
            'eqt_id': forms.HiddenInput()
        }


class MorForm(forms.ModelForm):

    class Meta:
        model = models.MorMooringSetups
        labels = get_descriptions(model)
        fields = labels.keys()
        widgets = {
            'mor_additional_equipment': forms.Textarea(attrs={"rows": 2}),
            'mor_general_moor_description': forms.Textarea(attrs={"rows": 2}),
            'more_notes': forms.Textarea(attrs={"rows": 2}),
        }


class PrmForm(forms.ModelForm):

    class Meta:
        model = models.PrmParameterCode
        labels = get_descriptions(model)
        fields = labels.keys()
        widgets = {
            'prm_id': forms.HiddenInput()
        }


class PrjForm(forms.ModelForm):

    class Meta:
        model = models.PrjProjects
        labels = get_descriptions(model)
        fields = labels.keys()
        widgets = {
            'prj_descrption': forms.Textarea(attrs={"rows": 2}),
        }


class RecForm(forms.ModelForm):

    class Meta:
        model = models.RecRecordingEvents
        labels = get_descriptions(model)
        fields = labels.keys()
        widgets = {
            'rec_date_of_system_chk': forms.DateInput(attrs={"type": "date"}),
            'rec_date_first_recording': forms.DateInput(attrs={"type": "date"}),
            'rec_date_last_recording': forms.DateInput(attrs={"type": "date"}),
            'rec_date_data_download': forms.DateInput(attrs={"type": "date"}),
            'rec_date_data_backed_up': forms.DateInput(attrs={"type": "date"}),
            'rec_first_in_water': forms.DateInput(attrs={"type": "date"}),
            'rec_last_in_water': forms.DateInput(attrs={"type": "date"}),
        }


class RscForm(forms.ModelForm):

    class Meta:
        model = models.RscRecordingSchedules
        labels = get_descriptions(model)
        fields = labels.keys()


class RstForm(forms.ModelForm):

    class Meta:
        model = models.RstRecordingStage
        labels = get_descriptions(model)
        fields = labels.keys()


class RttForm(forms.ModelForm):

    class Meta:
        model = models.RttTimezoneCode
        labels = get_descriptions(model)
        fields = labels.keys()
        widgets = {
            'rtt_id': forms.HiddenInput(),
        }


class SetForm(forms.ModelForm):

    class Meta:
        model = models.SetStationEventCode
        labels = get_descriptions(model)
        fields = labels.keys()
        widgets = {
            'set_id': forms.HiddenInput(),
            'set_description': forms.Textarea(attrs={"rows": 2}),
        }


class SteForm(forms.ModelForm):

    class Meta:
        model = models.SteStationEvents
        labels = get_descriptions(model)
        fields = labels.keys()
        widgets = {
            'ste_date': forms.DateInput(attrs={"type": "date"}),
            'ste_instrument_cond': forms.Textarea(attrs={"rows": 2}),
            'ste_weather_cond': forms.Textarea(attrs={"rows": 2}),
            'ste_logs': forms.Textarea(attrs={"rows": 2}),
            'ste_notes': forms.Textarea(attrs={"rows": 2}),
        }


class StnForm(forms.ModelForm):

    class Meta:
        model = models.StnStations
        labels = get_descriptions(model)
        fields = labels.keys()
        widgets = {
            'stn_notes': forms.Textarea(attrs={"rows": 2}),
        }


class TeaForm(forms.ModelForm):

    class Meta:
        model = models.TeaTeamMembers
        labels = get_descriptions(model)
        fields = labels.keys()
