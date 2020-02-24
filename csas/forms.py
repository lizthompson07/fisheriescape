from django import forms

from . import models


class ContactForm(forms.ModelForm):
    class Meta:
        model = models.ConContact
        exclude = []
        widget = {
        }


class MeetingForm(forms.ModelForm):
    class Meta:
        model = models.MetMeeting
        exclude = []
        widget = {
        }


class PublicationForm(forms.ModelForm):
    class Meta:
        model = models.PubPublication
        exclude = []
        widget = {
        }


class RequestForm(forms.ModelForm):
    class Meta:
        model = models.ReqRequest
        exclude = []
        widget = {
        }


class OtherForm(forms.ModelForm):
    class Meta:
        model = models.OthOther
        exclude = []
        widget = {
        }


