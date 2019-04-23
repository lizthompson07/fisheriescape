from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from . import models
from shared_models import models as shared_models


class TicketForm(forms.ModelForm):
    generic_file_to_load = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = models.Ticket
        exclude = ['notes_html', "resolved_email_date", 'notes', "date_opened", "date_modified",
                   "date_closed", "fiscal_year", "assigned_to"]
        widgets = {
            'date_closed': forms.DateInput(attrs={'type': 'date'}),
            'sd_date_logged': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': '5'}),
        }
        labels = {
            'app': _("Application name (if applicable)"),
            'dm_assigned': _("Assign ticket to")
        }

    def __init__(self, *args, **kwargs):
        USER_CHOICES = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                        User.objects.all().order_by("last_name", "first_name")]
        USER_CHOICES.insert(0, tuple((None, "---")))
        STAFF_USER_CHOICES = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                              User.objects.filter(is_staff=True).order_by("last_name", "first_name")]
        # STAFF_USER_CHOICES.insert(0, tuple((None, "---")))
        SECTION_CHOICES = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.all().order_by("division__branch__region", "division__branch", "division", "name")]
        SECTION_CHOICES.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['primary_contact'].choices = USER_CHOICES
        self.fields['sd_primary_contact'].choices = USER_CHOICES
        self.fields['dm_assigned'].choices = STAFF_USER_CHOICES
        self.fields['section'].choices = SECTION_CHOICES


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        exclude = [
            'notes_html',
            "resolved_email_date",
            'notes',
            "date_opened",
            "date_modified",
            "date_closed",
            "fiscal_year",
            "people_notes",
            'sd_ref_number',
            'sd_ticket_url',
            'sd_primary_contact',
            'sd_description',
            'sd_date_logged',
            'financial_follow_up_needed',
            'financial_coding',
            'estimated_cost',
            'assigned_to',
            'section',
        ]
        widgets = {
            'date_closed': forms.DateInput(attrs={'type': 'date'}),
            'sd_date_logged': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': '5'}),
            'primary_contact': forms.HiddenInput(),
            'status': forms.HiddenInput(),
        }
        labels = {
            'app': _("Application name (if applicable)"),
            'description': _("Feedback details"),
            'title': _("Subject"),
        }


class TicketNoteForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ("notes", "date_modified")
        widgets = {
            'date_modified': forms.HiddenInput(),
        }


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = "__all__"
        widgets = {
            'ticket': forms.HiddenInput(),
        }


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = models.FollowUp
        fields = "__all__"
        widgets = {
            'ticket': forms.HiddenInput(),
            'created_date': forms.HiddenInput(),
            'created_by': forms.HiddenInput(),
        }
