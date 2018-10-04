from django import forms
from django.core import validators
from . import models

class TagForm(forms.ModelForm):
    class Meta:
        model = models.Tag
        fields = ("__all__")
        labels={
            'tag':"Tag Name",
        }

class ServiceDeskTicketForm(forms.ModelForm):
    class Meta:
        model = models.ServiceDeskTicket
        fields = ("__all__")
        labels={
            'ref_number':"Reference Number",
        }
        widgets = {
            'date_logged':forms.DateInput(attrs={'type': 'date'}),
            'description':forms.Textarea(attrs={'rows': '5'}),
        }


class TicketForm(forms.ModelForm):
    primary_contact_email = forms.EmailField()
    field_order = [
        'title',
        'primary_contact',
        'primary_contact_email',
        'section',
        'request_type',
        'status',
        'priority',
        'description',
        'service_desk_ticket',
        'financial_coding',
        'date_closed',
    ]

    class Meta:
        model = models.Ticket
        exclude = ['notes_html','people','tags', "resolved_email_date", 'notes',"date_opened","date_modified"]
        widgets = {
            'date_closed':forms.DateInput(attrs={'type': 'date'}),
            'description':forms.Textarea(attrs={'rows': '5'}),
        }




class TicketNoteForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ("notes", "date_modified")
        widgets = {
            'date_modified':forms.HiddenInput(),
        }


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = "__all__"
        widgets = {
            'ticket':forms.HiddenInput(),
        }


class FilterForm(forms.Form):
    SECTION_CHOICES=[]

    for section in models.Section.objects.all():
        SECTION_CHOICES.append(tuple((section.id,section.section_name)))

    initial = tuple(('----','----'))

    SECTION_CHOICES.insert(0,initial)
    status_choices = list(models.Ticket.STATUS_CHOICES)
    status_choices.insert(0,initial)

    section = forms.ChoiceField(choices=SECTION_CHOICES, initial=initial)
    ticket_status = forms.ChoiceField(choices=status_choices, initial=initial)
