from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
###
from . import models
from . import forms
from . import filters
from . import emails


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'ihub/close_me.html'

def not_in_ihub_group(user):
    if user:
        return user.groups.filter(name='ihub_access').count() != 0

class iHubAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return not_in_ihub_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class IndexTemplateView(iHubAccessRequiredMixin, TemplateView):
    template_name = 'ihub/index.html'


# ENTRY #
#########

class EntryListView(iHubAccessRequiredMixin, FilterView):
    template_name = "ihub/entry_list.html"
    model = models.Entry
    filterset_class = filters.EntryFilter


class EntryDetailView(iHubAccessRequiredMixin, DetailView):
    model = models.Entry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'title',
            'organization',
            'status',
            'sector',
            'entry_type',
            'initial_date',
            'leads',
            'region',
            'funding_needed',
            'funding_requested',
            'amount_expected',
            'transferred',
            'amount_transferred',
            'fiscal_year',
            'funding_purpose',
            'date_last_modified',
            'date_created',
            'last_modified_by',
            'created_by',
        ]
        return context


class EntryUpdateView(iHubAccessRequiredMixin, UpdateView):
    model = models.Entry
    form_class = forms.EntryForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class EntryCreateView(iHubAccessRequiredMixin, CreateView):
    model = models.Entry
    form_class = forms.EntryCreateForm

    def form_valid(self, form):
        self.object = form.save()

        # create a new email object
        email = emails.NewEntryEmail(self.object)
        # send the email object
        if settings.MY_ENVR != 'dev':
            send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
                      recipient_list=email.to_list, fail_silently=False, )
        else:
            print('not sending email since in dev mode')
        messages.success(self.request, "The entry has been submitted and an email has been sent to the Indigenous Hub Coordinator!")
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'created_by': self.request.user
        }


class EntryDeleteView(iHubAccessRequiredMixin, DeleteView):
    model = models.Entry
    success_url = reverse_lazy('ihub:entry_list')
    success_message = _('The entry was successfully deleted!')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# NOTES #
#########

class NoteCreateView(iHubAccessRequiredMixin, CreateView):
    model = models.EntryNote
    template_name = 'ihub/note_form_popout.html'
    form_class = forms.NoteForm

    def get_initial(self):
        entry = models.Entry.objects.get(pk=self.kwargs['entry'])
        return {
            'author': self.request.user,
            'entry': entry,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = models.Entry.objects.get(id=self.kwargs['entry'])
        context['entry'] = entry
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


class NoteUpdateView(iHubAccessRequiredMixin, UpdateView):
    model = models.EntryNote
    template_name = 'ihub/note_form_popout.html'
    form_class = forms.NoteForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('ihub:close_me'))


def note_delete(request, pk):
    object = models.EntryNote.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The note has been successfully deleted from the entry."))
    return HttpResponseRedirect(reverse_lazy("ihub:entry_detail", kwargs={"pk": object.entry.id}))

