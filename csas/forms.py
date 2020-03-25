from django import forms
from . import models
from . import custom_widgets


class RequestForm(forms.ModelForm):
    class Meta:
        model = models.ReqRequest

        # fields shown on screen
        # fields = ("assigned_request_ID", "title",)    # only show listed fields
        # fields = ["assigned_request_ID", "title"]     # [" "] is the same as (" ",)
        exclude = ["assigned_req_id"]                   # show all fields except listed fields

        # use some widgets
        widgets = {
            # "region": forms.Select(attrs={"class": "chosen-select-contains"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['program_contact'].widgets = forms.Select(choices=models.ConContact.objects.all())
        self.fields['adviser_submission'].widgets = forms.DateField(help_text="Select date")


class ContactForm(forms.ModelForm):
    class Meta:
        model = models.ConContact
        exclude = []
        widgets = {
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # a lot being done here.
        # 1. Get all contact objects with models.ConContact.objects.all()
        # 2. Get all of the existing affiliation values for those objects with .values_list('affiliation')
        # 3. Remove duplicate affiliations with .distinct()
        # 4. iterate through the 'queryset' with for a in __returned queryset__
        # 6. save all the created tuples as an array with affilitations = [tuple]
        affiliations = [a[0] for a in models.ConContact.objects.all().order_by('affiliation').values_list('affiliation').distinct()]

        # pass the list of values to the select widget
        self.fields['affiliation'].widget = custom_widgets.SelectAdd(data_list=affiliations, name="affiliation-list")


class MeetingForm(forms.ModelForm):
    class Meta:
        model = models.MetMeeting
        exclude = []
        widgets = {
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['program_contact'].wigets = forms.Select(choices=models.ConContact.objects.all())


class PublicationForm(forms.ModelForm):
    class Meta:
        model = models.PubPublication
        exclude = []
        widgets = {
        }


# class RequestForm(forms.ModelForm):
#    class Meta:
#        model = models.ReqRequest
#        exclude = []
#        widgets = {
#        }


# class OtherForm(forms.ModelForm):
#    class Meta:
#        model = models.OthOther
#        exclude = []
#        widgets = {
#        }


