from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash, login, authenticate
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
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
from inventory import models as inventory_models


# Create your views here.

class IndexView(TemplateView):
    template_name = 'accounts/index.html'

# class DataFlowTemplateView(TemplateView):
#     template_name = 'landing/dataflow.html'

class DeniedAccessTemplateView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages.error(self.request, "Sorry, you are not authorized to view this page. Please contact the site administrator to request access.")
        return  context

# class DataFlowTemplateView(TemplateView):
#     template_name = 'landing/dataflow.html'


class UserLoginView(LoginView):
    template_name = "registration/login.html"

class UserUpdateView(UpdateView):
    model = get_user_model()
    form_class = forms.UserAccountForm
    template_name = 'registration/user_form.html'
    success_url = reverse_lazy('index')

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
                update_session_auth_hash(request, user)  # Important!

                # the user should be added to the People object of data inventory
                # user_instance = User.objects.get(pk=user.id) #for some reason, the create() method does not want to accept the user instance
                # new_person = inventory_models.Person.objects.create(
                #     user=user_instance,
                #     full_name="{}, {}".format(user.last_name, user.first_name),
                #     organization_id=6
                # )
                user.groups.add(group)

                messages.success(request, 'Your password was successfully updated!')
                return redirect('index' )
        else:
            form = SetPasswordForm(request.user)
        return render(request, 'registration/account_verified.html', {
            'form': form
    })


def resend_verification_email(request, email):
    group = Group.objects.get(name='verified')
    user = User.objects.get(email__iexact=email)
    try:
        user.groups.remove(group)
    except:
        pass
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
            return HttpResponseRedirect(reverse('index' ))
    else:
        form = forms.AccountRequestForm()
    return render(request, 'registration/account_request_form.html', {
        'form': form,
    })

def signup(request):
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            print(123)
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
    try:
        uid = force_text(urlsafe_base64_decode(force_bytes(uidb64)))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        messages.success(request, 'Congrats! Your account has been successfully verified')
        return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponse('Activation link is invalid!')

# def UserResetPassword(request):
#     form = UserForgotPasswordForm(None, request.POST)
#     if request.method == 'POST':
#         if form.is_valid():
#             form.save(from_email='blah@blah.com', email_template_name='path/to/your/email_template.html')

#
class UserPassWordResetView(PasswordResetView):
    template_name = "registration/user_password_reset_form.html"
    success_message = "An email has been sent!"

    def get_success_url(self, **kwargs):
        messages.success(self.request, self.success_message)
        return reverse('index')
#
class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/user_password_reset_confirm.html"

    def get_success_url(self, **kwargs):
        messages.success(self.request, "Your password has been successfully reset! Please try logging in with your new password.")
        return reverse('index')
#
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
