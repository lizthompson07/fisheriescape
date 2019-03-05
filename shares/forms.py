from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext as _
from django.contrib.auth.models import User as AuthUser


from . import models

YES_NO_CHOICES = (
    (True, _("Yes")),
    (False, _("No")),
)

class ServerForm(forms.ModelForm):
    class Meta:
        model = models.Server
        fields = "__all__"

        widgets = {
            'notes': forms.Textarea(attrs={"rows": 3}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = "__all__"

        widgets = {
            'notes': forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        USER_CHOICES = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                        AuthUser.objects.all().order_by("last_name", "first_name")]
        USER_CHOICES.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['user'].choices = USER_CHOICES

class ShareForm(forms.ModelForm):
    class Meta:
        model = models.Share
        fields = "__all__"

        widgets = {
            'notes': forms.Textarea(attrs={"rows": 3}),
        }
