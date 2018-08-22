from django.views.generic import TemplateView, UpdateView, CreateView #,ListView, DetailView, CreateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.core.mail import send_mail

from . import forms
from . import emails

# Create your views here.

class IndexView(TemplateView):
    template_name = 'accounts/index.html'

class DataFlowTemplateView(TemplateView):
    template_name = 'landing/dataflow.html'

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
            return redirect('landing:home' )
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })


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
