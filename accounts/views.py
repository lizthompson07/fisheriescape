from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.backends import UserModel
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView, PasswordResetView, INTERNAL_RESET_SESSION_TOKEN
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView, FormView  # ,ListView, DetailView, CreateView, DeleteView

from dm_apps.utils import custom_send_mail
from shared_models.views import CommonUpdateView
from . import emails
from . import forms
from . import models
from .auth_helper import get_sign_in_url, get_token_from_code, remove_user_and_token
from .graph_helper import get_user
from .tokens import account_activation_token, otp_token_generator
from .utils import send_activation_email


def sign_in(request):
    # Get the sign-in URL
    sign_in_url, state = get_sign_in_url()
    # Save the expected state so we can validate in the callback
    request.session['auth_state'] = state
    # Redirect to the Azure sign-in page
    return HttpResponseRedirect(sign_in_url)


def callback(request):
    # Get the state saved in session
    expected_state = request.session.pop('auth_state', '')
    # Make the token request
    token = get_token_from_code(request.get_full_path(), expected_state)

    # Get the user's profile
    user = get_user(token)
    my_email = user.get("mail") if user.get("mail") else user.get("userPrincipalName")
    my_first_name = user.get("givenName")
    my_last_name = user.get("surname")
    my_job = user.get("jobTitle")
    my_phone = user.get("businessPhones")

    try:
        my_user = User.objects.get(email__iexact=my_email)
        my_user.first_name = my_first_name
        my_user.last_name = my_last_name
        my_user.save()
    except User.DoesNotExist:
        my_user = User.objects.create(
            username=my_email,
            email=my_email,
            first_name=my_first_name,
            last_name=my_last_name,
            is_active=True,
            password="pbkdf2_sha256$120000$ctoBiOUIJMD1$DWVtEKBlDXXHKfy/0wKCpcIDYjRrKfV/wpYMHKVrasw=",
        )
    finally:
        my_profile = my_user.profile
        my_profile.position_eng = my_job
        my_profile.position_fre = my_job
        my_profile.phone = my_phone
        try:
            my_profile.save()
        except:
            print("there was an error in trying to copy over the user's profile data from AAD")

    login(request, my_user)
    return HttpResponseRedirect(reverse('index'))


class CloserTemplateView(TemplateView):
    template_name = 'accounts/close_me.html'


# This is a good one. It should be able to replace all others with the message arg.
def access_denied(request, message=None):
    my_url = f'{reverse("tickets:bug_create")}?permission_request=true&app={request.GET.get("app")}'
    a_tag = mark_safe(
        '<a pop-href="{}" href="#" class="btn btn-sm btn-primary badge request-access-button">{}</a>'.format(my_url, _("Request access")))
    if not message:
        message = _("Sorry, you are not authorized to view this page.")
    denied_message = "{} {}".format(message, a_tag)
    messages.error(request, mark_safe(denied_message))
    # send user back to the page that they came from
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ProfileUpdateView(CommonUpdateView):
    model = models.Profile
    form_class = forms.ProfileForm
    success_url = reverse_lazy("index")
    template_name = 'accounts/profile_form.html'
    home_url_name = "index"

    def get_h1(self):
        return _("DM Apps Profile for {user}").format(user=self.request.user)

    def get_initial(self):
        user = self.get_object().user
        return dict(first_name=user.first_name, last_name=user.last_name, email=user.email)

    def get_object(self, queryset=None):
        user = self.request.user
        try:
            profile = models.Profile.objects.get(user=user)
        except models.Profile.DoesNotExist:
            print("Profile does not exist, creating Profile")
            profile = models.Profile(user=user)

        return profile

    def form_valid(self, form):
        profile = form.save()
        user = profile.user
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.email = form.cleaned_data["email"]
        user.username = form.cleaned_data["email"]
        user.save()
        messages.success(self.request, _("Successfully updated!"))
        return super().form_valid(form)


class UserLoginView(PasswordResetView):
    template_name = "registration/login.html"
    form_class = forms.DMAppsEmailLoginForm
    from_email = settings.SITE_FROM_EMAIL
    subject_template_name = 'registration/dm_apps_email_login_subject.txt'
    email_template_name = 'registration/dm_apps_email_login_email.html'
    success_url = reverse_lazy('index')

    def get_initial(self):
        initial = dict(email=self.request.GET.get("email"))
        return initial

    def dispatch(self, request, *args, **kwargs):
        if settings.AZURE_AD:
            return HttpResponseRedirect(reverse("accounts:azure_login"))
        else:
            return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        user = get_object_or_404(User, email__iexact=form.cleaned_data["email"])
        messages.success(
            self.request, f'<span class="mdi mdi-email-outline mr-3 lead"></span>' +
                          _("An e-mail with a login link has been sent to you! ") +
                          _("To enter a code manually, click ") +
                          '<a href="{}">{}</a>'.format(reverse("accounts:regular_callback", args=[
                              urlsafe_base64_encode(force_bytes(user.pk)),
                              "manual"
                          ]), _("here"))
        )
        return HttpResponseRedirect(self.get_success_url())


class CallBack(FormView):
    token_generator = otp_token_generator
    reset_url_token = 'cleared'
    manual_url_token = 'manual'
    success_url = reverse_lazy("index")
    invalid_token_msg = gettext_lazy("Sorry the link you used to sign in with is not valid!")
    form_class = forms.OTPForm
    template_name = 'registration/token_form.html'

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        # this gets the using based on the encrypted pk
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']

            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    self.user.is_active = True
                    self.user.save()
                    login(self.request, self.user)
                else:
                    messages.error(self.request, self.invalid_token_msg)

            elif token == self.manual_url_token:
                return super().dispatch(request, *args, **kwargs)


            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token)
                    return HttpResponseRedirect(redirect_url)
                else:
                    messages.error(self.request, self.invalid_token_msg)
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.error(self.request, self.invalid_token_msg)
        return HttpResponseRedirect(self.get_success_url())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
            user = None
        return user

    def form_valid(self, form):
        token = form.cleaned_data["otp"]
        if self.token_generator.check_token(self.user, token):
            # If the token is valid, display the password reset form.
            self.validlink = True
            self.user.is_active = True
            self.user.save()
            login(self.request, self.user)
        else:
            messages.error(self.request, self.invalid_token_msg)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.user:
            context["user_email"] = self.user.email
        return context


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("index")

    def dispatch(self, request, *args, **kwargs):
        remove_user_and_token(request)
        return super().dispatch(request, *args, **kwargs)


def signup(request):
    if request.method == 'POST':
        form = forms.UserAccountForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.is_active = False
            user.save()
            send_activation_email(user, request)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = forms.UserAccountForm()
    return render(request, 'registration/signup.html', {'form': form})


def resend_activation_email(request):
    if request.method == 'POST':
        form = forms.ResendVerificationEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = get_object_or_404(User, email__iexact=email)
            user.username = user.email
            user.save()
            send_activation_email(user, request)
        return HttpResponseRedirect(reverse('index'))
    else:
        form = forms.ResendVerificationEmailForm(initial=dict(email=request.GET.get("email")))
    return render(request, 'registration/resend_verification_email.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
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

#
# class RequestAccessFormView(LoginRequiredMixin, FormView):
#     template_name = "accounts/request_access_form_popout.html"
#     form_class = forms.RequestAccessForm
#
#     def get_initial(self):
#         user = self.request.user
#         return {
#             'first_name': user.first_name,
#             'last_name': user.last_name,
#             'email': user.email,
#             'user_id': user.id,
#         }
#
#     def form_valid(self, form):
#         context = {
#             "first_name": form.cleaned_data["first_name"],
#             "last_name": form.cleaned_data["last_name"],
#             "email": form.cleaned_data["email"],
#             "user_id": form.cleaned_data["user_id"],
#             "application": form.cleaned_data["application"],
#             "optional_comment": form.cleaned_data["optional_comment"],
#         }
#         email = emails.RequestAccessEmail(context, self.request)
#         # send the email object
#         custom_send_mail(
#             subject=email.subject,
#             html_message=email.message,
#             from_email=email.from_email,
#             recipient_list=email.to_list
#         )
#         messages.success(self.request,
#                          message="your request has been sent to the site administrator")
#         return HttpResponseRedirect(reverse('shared_models:close_me'))
