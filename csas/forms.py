from django import forms

from . import models

from . import custom_widgets


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
        # 5. Convert the iteration into a tuple with (a[0], a[0])
        # 6. save all the created tuples as an array with affilitations = [tuple]
        affiliations = [a[0] for a in models.ConContact.objects.all().values_list('affiliation').distinct()]

        # pass the list of values to the select widget
        self.fields['affiliation'].widget = custom_widgets.SelectAdd(data_list=affiliations, name="affiliation-list")


class MeetingForm(forms.ModelForm):
    class Meta:
        model = models.MetMeeting
        exclude = []
        widgets = {
            "program_contact": forms.Select(choices=models.ConContact.objects.all())
        }


class PublicationForm(forms.ModelForm):
    class Meta:
        model = models.PubPublication
        exclude = []
        widgets = {
        }


class RequestForm(forms.ModelForm):
    class Meta:
        model = models.ReqRequest
        exclude = []
        widgets = {
        }


class OtherForm(forms.ModelForm):
    class Meta:
        model = models.OthOther
        exclude = []
        widgets = {
        }


