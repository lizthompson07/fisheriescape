from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, UserModel, _unicode_ci_compare
from django.contrib.auth.models import User
from django.template import loader
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext_lazy

from dm_apps.utils import custom_send_mail
from . import models
from .tokens import otp_token_generator

chosen_js = {"class": "chosen-select-contains"}

try:
    from dm_apps import my_conf as local_conf
except (ModuleNotFoundError, ImportError):
    from dm_apps import default_conf as local_conf


# from django.contrib.auth.forms import UserCreationForm


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label=_("First name"))
    last_name = forms.CharField(label=_("Last name"))
    email = forms.EmailField(label=_("Email"))
    field_order = ("first_name", "last_name", "email",)

    class Meta:
        model = models.Profile
        fields = ('position_eng', 'position_fre', 'phone', 'language', 'section')

    def __init__(self, *args, **kwargs):
        from shared_models import models as shared_models
        super().__init__(*args, **kwargs)
        section_choices = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.all().order_by("division__branch__region", "division__branch",
                                                                        "division", "name")]
        section_choices.insert(0, tuple((None, "---")))

        self.fields["section"].choices = section_choices
        self.fields["section"].widget.attrs = chosen_js

    def clean_email(self):
        new_email = self.cleaned_data['email']
        old_email = self.instance.user.email
        if new_email != old_email and User.objects.filter(email__iexact=new_email).exists():
            raise forms.ValidationError(mark_safe(_("There is already a DM Apps account with this email address.")))
        return new_email


class UserAccountForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    def clean_email(self):
        new_email = self.cleaned_data['email']
        user_qs = User.objects.filter(email__iexact=new_email)
        if user_qs.exists():
            user = user_qs.first()
            if user.is_active:
                url_redirect = reverse("accounts:login")
                raise forms.ValidationError(mark_safe(
                    _("You already have an account on DM Apps. Please sign in <a href='{url}'>HERE</a>").format(url=url_redirect)))
            else:
                url_redirect = reverse("accounts:resend_activation_email")
                raise forms.ValidationError(mark_safe(
                    _("There is already an account on DM Apps with this email address however it has not been validated. Please validate this account <a href='{url}'>HERE</a>").format(
                        url=url_redirect)))

        if new_email.lower().endswith("@dfo-mpo.gc.ca") == False:
            raise forms.ValidationError(
                _("Only DFO employees can register for an account. Please enter an email ending with '@DFO-MPO.GC.CA'"))

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return new_email


class AccountRequestForm(forms.Form):
    first_name = forms.CharField(label='First name', max_length=100)
    last_name = forms.CharField(label='Last name', max_length=100)
    email = forms.EmailField(label='Email address')
    reason_for_request = forms.CharField(widget=forms.Textarea)


class ResendVerificationEmailForm(forms.Form):
    email = forms.EmailField(required=True)


class RequestAccessForm(forms.Form):
    # we only want the text from the choices of apps
    APPLICATION_CHOICES = [(app_key, local_conf.APP_DICT[app_key]['name']) for app_key in local_conf.APP_DICT]
    APPLICATION_CHOICES.insert(0, (None, "-----"))

    first_name = forms.CharField(label='First name', max_length=100)
    last_name = forms.CharField(label='Last name', max_length=100)
    email = forms.EmailField(label='Email address')
    user_id = forms.CharField(widget=forms.HiddenInput())
    application = forms.ChoiceField(label='Requesting access to which app', choices=APPLICATION_CHOICES)
    optional_comment = forms.CharField(required=False, label="Details")


class DMAppsEmailLoginForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        custom_send_mail(
            html_message=body,
            subject=subject,
            from_email=from_email,
            recipient_list=[to_email]
        )

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(**{
            '%s__iexact' % email_field_name: email,
        })

        return (
            u for u in active_users
            if u.has_usable_password() and
               _unicode_ci_compare(email, getattr(u, email_field_name))
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields["email"].label = _("Please enter the DFO e-mail address associated with your account:")
        self.fields["email"].widget = forms.EmailInput(attrs={'autocomplete': 'email', "placeholder": _("Email")})

    # def clean_email(self):
    #     new_email = self.cleaned_data['email']
    #     if new_email.lower().endswith("@dfo-mpo.gc.ca") == False:
    #         raise forms.ValidationError(
    #             _("Please enter an email ending with '@dfo-mpo.gc.ca'"))
    #     if len([u for u in self.get_users(new_email)]) == 0:
    #         raise forms.ValidationError(_("This email address is not in the system. Please check the spelling or register for an account "))
    #     return new_email

    def clean_email(self):
        new_email = self.cleaned_data['email']
        if new_email.lower().endswith("@dfo-mpo.gc.ca") == False:
            raise forms.ValidationError(_("Only DFO employees can register for an account. Please enter an email ending with '@DFO-MPO.GC.CA'"))
        elif len([u for u in self.get_users(new_email)]) == 0:
            raise forms.ValidationError(_("This email address is not in the system. Please check the spelling or register for an account "))
        else:
            for user in self.get_users(new_email):
                if not user.is_active:
                    url_redirect = reverse("accounts:resend_activation_email")
                    raise forms.ValidationError(mark_safe(
                        _("This has not been activated. Please validate this account <a href='{url}?email={email}'>HERE</a>").format(
                            url=url_redirect, email=new_email)))

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return new_email

    def save(self, *args, **kwargs):
        kwargs["token_generator"] = otp_token_generator
        super().save(*args, **kwargs)


class OTPForm(forms.Form):
    otp = forms.CharField(required=True, label=gettext_lazy("Code"))
