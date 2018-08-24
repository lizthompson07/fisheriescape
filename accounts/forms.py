from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.urls import reverse

# from django.contrib.auth.forms import UserCreationForm

class UserAccountForm(forms.ModelForm):
    class Meta:
        # fields = ('username','first_name','last_name','email','password1','password2')
        model = get_user_model()
        fields = ('email','first_name','last_name')
        labels = {
            'email':"Username / Email address"
        }

class AccountRequestForm(forms.Form):
    first_name = forms.CharField(label='First name', max_length=100)
    last_name = forms.CharField(label='Last name', max_length=100)
    email = forms.EmailField(label='Email address')
    reason_for_request = forms.CharField(widget=forms.Textarea)


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required - a verification email will be sent to you once this form is submitted')

    class Meta:
        model = User
        fields = ( 'first_name', 'last_name','email', 'password1', 'password2')

    def clean_email(self):
        new_email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=new_email).count() > 0:
            url_redirect = reverse("password_reset")
            raise forms.ValidationError(mark_safe("This email address in already in our database. To reset your login credentials click <a href='{}'>HERE</a>".format(url_redirect)))
            # raise forms.ValidationError(_(mark_safe('An account already exists for this email address. <a href="#" class="email_error">Log in instead?</a>')))

        if new_email.lower().endswith("@dfo-mpo.gc.ca") == False:
            raise forms.ValidationError("Only DFO employees can register for an account. Please enter an email ending with '@DFO-MPO.GC.CA'")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return new_email


class UserForgotPasswordForm(PasswordResetForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("email")



# class SetUserPasswordForm(SetPasswordForm):

    # label='Reason for request'
