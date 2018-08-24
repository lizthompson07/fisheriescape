from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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
    email = forms.EmailField(max_length=200, help_text='Required')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')




    # label='Reason for request'
