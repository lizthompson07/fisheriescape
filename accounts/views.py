from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash, login, authenticate
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView, UpdateView, CreateView #,ListView, DetailView, CreateView, DeleteView

from .tokens import account_activation_token
from . import forms
from . import emails

# Create your views here.

class IndexView(TemplateView):
    template_name = 'accounts/index.html'

class DataFlowTemplateView(TemplateView):
    template_name = 'landing/dataflow.html'

class UserLoginView(LoginView):
    template_name = "registration/login.html"

class UserUpdateView(UpdateView):
    model = get_user_model()
    form_class = forms.UserAccountForm
    template_name = 'registration/user_form.html'
    success_url = reverse_lazy('landing:home')

    def form_valid(self, form):
        self.object.username = self.object.email
        return super().form_valid(form)

def change_password(request):
    # user_model = get_user_model()
    # print(user_model.id)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('index' )
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })

def account_verified(request):
    group = Group.objects.get(name='verified')
    if group in request.user.groups.all():
        messages.error(request, 'This account has already been verified')
        return redirect('index' )
    else:
        if request.method == 'POST':
            form = SetPasswordForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                user.groups.add(group)
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Your password was successfully updated!')
                return redirect('index' )
        else:
            form = SetPasswordForm(request.user)
        return render(request, 'registration/account_verified.html', {
            'form': form
    })


def resend_verification_email(request, email):
    user = User.objects.get(email__iexact=email)
    current_site = get_current_site(request)
    mail_subject = 'Activate your Gulf Region Data Management account.'
    message = render_to_string('registration/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid':force_text(urlsafe_base64_encode(force_bytes(user.pk))),
        'token':account_activation_token.make_token(user),
    })
    to_email = user.email
    from_email='DoNotReply@{}.com'.format(settings.WEB_APP_NAME)
    email = EmailMessage(
                mail_subject, message, to=[to_email], from_email=from_email,
    )
    if settings.MY_ENVR != 'dev':
        email.send()
    else:
        print('not sending email since in dev mode')
        print(message)

    return HttpResponse('A verification email has been sent. Please check your inbox.')


def account_request(request):
    if request.method == 'POST':
        form = forms.AccountRequestForm(request.POST)
        if form.is_valid():
            email = emails.AccountRequestEmail(form.cleaned_data)
            # send the email object
            send_mail( message='', subject=email.subject, html_message=email.message, from_email=email.from_email, recipient_list=email.to_list,fail_silently=False,)
            messages.success(request, 'An email with your request has been send to the application administrator')
            return HttpResponseRedirect(reverse('landing:home' ))
    else:
        form = forms.AccountRequestForm()
    return render(request, 'registration/account_request_form.html', {
        'form': form,
    })

def signup(request):
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your Gulf Region Data Management account.'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':force_text(urlsafe_base64_encode(force_bytes(user.pk))),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            from_email='DoNotReply@{}.com'.format(settings.WEB_APP_NAME)
            email = EmailMessage(
                        mail_subject, message, to=[to_email], from_email=from_email,
            )
            if settings.MY_ENVR != 'dev':
                email.send()
            else:
                print('not sending email since in dev mode')
                print(message)
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = forms.SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

def activate(request, uidb64, token):
    print(uidb64)
    # print(urlsafe_base64_decode(uidb64))
    print(force_bytes(uidb64))
    try:
        uid = force_text(urlsafe_base64_decode(force_bytes(uidb64)))
        print(uid)
        user = User.objects.get(pk=uid)
        print(user)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    print(token)
    print(user is not None)
    print(account_activation_token.check_token(user, token))
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponseRedirect(reverse('accounts:verified'))
    else:
        return HttpResponse('Activation link is invalid!')
