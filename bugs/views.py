from django.shortcuts import render
from django.views.generic import ListView,  UpdateView, DeleteView, CreateView, DetailView, TemplateView
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from django_filters.views import FilterView
from django.contrib import messages
from django.conf import settings

from . import models
from . import forms
from . import filters
from . import emails

class CloserTemplateView(TemplateView):
    template_name = 'bugs/close_me.html'

class BugListView(FilterView):
    # model = models.Ticket
    filterset_class = filters.BugFilter
    template_name = "bugs/bug_list.html"

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        try:
            self.kwargs["application"]
        except Exception as e:
            print("returning full, unadulterated bug list")
        else:
            if kwargs["data"] is None:
                kwargs["data"] = {
                    "resolved": False,
                    "application": self.kwargs["application"]
                 }

        return kwargs

class BugCreateView(LoginRequiredMixin,CreateView):
    template_name = "bugs/bug_form_popout.html"
    form_class = forms.BugCreateForm

    def get_initial(self):
        user = self.request.user.id
        return {
            'user': user,
            'application': self.kwargs['application']
            }

    def form_valid(self, form):
        self.object = form.save()
        # create a new email object
        email = emails.NewBugNotificationEmail(self.object, self.kwargs['application'])
        # send the email object
        if settings.PRODUCTION_SERVER:
            send_mail( message='', subject=email.subject, html_message=email.message, from_email=email.from_email, recipient_list=email.to_list,fail_silently=False,)
        else:
            print('not sending email since in dev mode')
        messages.success(self.request, message="The report has been logged and an email has been sent to the site administrator" )
        return HttpResponseRedirect(reverse('bugs:close_me'))

class BugDetailView(LoginRequiredMixin,DetailView):
    template_name = "bugs/bug_detail.html"
    fields = "__all__"
    model = models.Bug

class BugUpdateView(LoginRequiredMixin,UpdateView):
    form_class = forms.BugUpdateForm
    template_name = "bugs/bug_form.html"
    model = models.Bug
    success_url = reverse_lazy('bugs:bug_list')

class BugDeleteView(LoginRequiredMixin,DeleteView):
    model = models.Bug

    def get_success_url(self):
        try:
            self.kwargs["application"]
        except Exception as e:
            print("returning to full, unadulterated bug list")
            return reverse('bugs:bug_list')
        else:
            print("returning to full, unadulterated bug list")
            return reverse('bugs:bug_list_4_app', kwargs={"application":self.kwargs["application"]})


def bug_resolved(request, pk):
    bug = models.Bug.objects.get(pk=pk)
    bug.date_resolved = timezone.now()
    bug.save()

    return HttpResponseRedirect(reverse('bugs:bug_list_4_app', kwargs={"application":bug.application}))
