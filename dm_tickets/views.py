from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, UpdateView, DeleteView, CreateView, DetailView
from django_filters.views import FilterView
from shutil import copyfile
import os

from . import models
from . import forms
from . import filters
from . import reports
from . import emails


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'dm_tickets/close_me.html'


# Ticket #
##########

class TicketListView(FilterView):
    filterset_class = filters.TicketFilter
    template_name = "dm_tickets/ticket_list.html"
    queryset = models.Ticket.objects.annotate(
        search_term=Concat('id', 'title', 'description', 'notes', output_field=TextField()))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["my_object"] = models.Ticket.objects.first()
        context["field_list"] = [
            'id',
            'date_modified',
            'priority',
            'dm_assigned',
            'app',
            'title',
            'request_type',
            'section',
            'status',
            'primary_contact',
            'sd_ref_number',
        ]
        return context

    # def get_filterset_kwargs(self, filterset_class):
    #     kwargs = super().get_filterset_kwargs(filterset_class)
    #     if kwargs["data"] is None:
    #         kwargs["data"] = {"status": 5}
    #     return kwargs


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = models.Ticket
    login_url = '/accounts/login_required/'
    template_name = "dm_tickets/ticket_detail.html"

    # form_class = forms.TicketDetailForm

    def get_context_data(self, **kwargs):
        context = super(TicketDetailView, self).get_context_data(**kwargs)
        context['email'] = emails.TicketResolvedEmail(self.object)
        context["field_group_1"] = [
            "primary_contact",
            "assigned_to",
            "app",
            "section",
            "status",
            "priority",
            "request_type",
        ]

        context["field_group_2"] = [
            "financial_coding",
            "description",
            "notes_html",
            "people_notes",
        ]

        context["field_group_3"] = [
            "date_opened",
            "date_modified",
            "date_closed",
            "resolved_email_date",
        ]

        context["field_group_4"] = [
            "sd_ref_number",
            "sd_ticket_url",
            "sd_primary_contact",
            "sd_description",
            "sd_date_logged",
        ]
        return context


def send_resolved_email(request, ticket):
    # grab a copy of the resource
    my_ticket = models.Ticket.objects.get(pk=ticket)
    # create a new email object
    email = emails.TicketResolvedEmail(my_ticket)
    # send the email object
    if settings.PRODUCTION_SERVER:
        send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email, recipient_list=email.to_list,
                  fail_silently=False, )
    else:
        print('not sending email since in dev mode')
        print(email)

    my_ticket.resolved_email_date = timezone.now()
    my_ticket.save()
    messages.success(request, "the email has been sent!")
    return HttpResponseRedirect(reverse('tickets:detail', kwargs={'pk': ticket}))


def mark_ticket_resolved(request, ticket):
    my_ticket = models.Ticket.objects.get(pk=ticket)
    my_ticket.status_id = 1
    my_ticket.save()
    return HttpResponseRedirect(reverse('tickets:detail', kwargs={'pk': ticket}))


def mark_ticket_active(request, ticket):
    my_ticket = models.Ticket.objects.get(pk=ticket)
    my_ticket.status_id = 2
    my_ticket.date_closed = None
    my_ticket.save()
    return HttpResponseRedirect(reverse('tickets:detail', kwargs={'pk': ticket}))


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Ticket
    template_name = "dm_tickets/ticket_form.html"
    login_url = '/accounts/login_required/'
    form_class = forms.TicketForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Ticket
    success_url = reverse_lazy('tickets:list')
    login_url = '/accounts/login_required/'


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = models.Ticket
    login_url = '/accounts/login_required/'
    form_class = forms.TicketForm

    def get_initial(self):
        return {'primary_contact': self.request.user}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        self.object = form.save()

        # create a new email object
        email = emails.NewTicketEmail(self.object)
        # send the email object
        if settings.PRODUCTION_SERVER:
            send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
                      recipient_list=email.to_list, fail_silently=False, )
        else:
            print('not sending email since in dev mode')
            print(email)

        messages.success(self.request, "The new ticket has been logged and a confirmation email has been sent!")

        # check to see if a generic file should be appended
        if form.cleaned_data["generic_file_to_load"]:
            return HttpResponseRedirect(reverse_lazy("tickets:add_generic_file",
                                                     kwargs={"ticket": self.object.id, "type": form.cleaned_data["generic_file_to_load"]}))

        # if nothing, just go to detail page
        else:
            return HttpResponseRedirect(self.get_success_url())


class TicketCreateViewPopout(LoginRequiredMixin, CreateView):
    model = models.Ticket
    login_url = '/accounts/login_required/'
    form_class = forms.FeedbackForm
    template_name = "dm_tickets/ticket_form_popout.html"

    def get_initial(self):
        my_dict = {
            'primary_contact': self.request.user,
            'request_type': 19,
        }
        try:
            self.kwargs['app']
        except KeyError:
            pass
        else:
            my_dict["app"] = self.kwargs['app']

        return my_dict

    def form_valid(self, form):
        self.object = form.save()

        # create a new email object
        email = emails.NewTicketEmail(self.object)
        # send the email object
        if settings.PRODUCTION_SERVER:
            send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
                      recipient_list=email.to_list, fail_silently=False, )
        else:
            print('not sending email since in dev mode')
            print(email)
        # messages.success(self.request,
        #                  _("The feedback form has been successfully submitted. You should receive an email confirmation momentarily!"))
        return HttpResponseRedirect(reverse_lazy('tickets:detail_pop', kwargs={"pk": self.object.id}))


class TicketDetailViewPopout(LoginRequiredMixin, DetailView):
    model = models.Ticket
    template_name = "dm_tickets/ticket_detail_popout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = emails.TicketResolvedEmail(self.object)
        context["field_group_1"] = [
            "app",
            "priority",
            "request_type",
        ]

        context["field_group_2"] = [
            "financial_coding",
            "description",
            "notes_html",
            "people_notes",
        ]

        context["field_group_3"] = [
            "date_opened",
            "date_modified",
            "date_closed",
            "resolved_email_date",
        ]

        context["field_group_4"] = [
            "sd_ref_number",
            "sd_ticket_url",
            "sd_primary_contact",
            "sd_description",
            "sd_date_logged",
        ]
        return context


class TicketNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Ticket
    template_name = "dm_tickets/ticket_note_form.html"
    login_url = '/accounts/login_required/'
    form_class = forms.TicketNoteForm


# Files #
#########

class FileCreateView(LoginRequiredMixin, CreateView):
    model = models.File
    # fields = '__all__'
    template_name = 'dm_tickets/file_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.FileForm

    def get_initial(self):
        ticket = models.Ticket.objects.get(pk=self.kwargs['ticket'])
        return {'ticket': ticket}

    def form_valid(self, form):
        self.object = form.save()

        # create a new email object
        email = emails.NewFileAddedEmail(self.object)
        # send the email object
        if settings.PRODUCTION_SERVER:
            send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
                      recipient_list=email.to_list, fail_silently=False, )
        else:
            print('not sending email since in dev mode')

        return HttpResponseRedirect(reverse('tickets:close_me'))


class FileUpdateView(LoginRequiredMixin, UpdateView):
    model = models.File
    fields = '__all__'
    template_name = 'dm_tickets/file_form_popout.html'
    # form_class = forms.StudentCreateForm


class FileDetailView(LoginRequiredMixin, UpdateView):
    model = models.File
    fields = '__all__'
    template_name = 'dm_tickets/file_detail_popout.html'

    # form_class = forms.TagForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class FileDeleteView(LoginRequiredMixin, DeleteView):
    model = models.File
    template_name = 'dm_tickets/file_confirm_delete_popout.html'

    # form_class = forms.StudentCreateForm

    def get_success_url(self):
        return reverse_lazy('tickets:close_me')


def add_generic_file(request, ticket, type):
    if type == "monitor":
        filename = "5166_Hardware_Request_Monitor.pdf"
    elif type == "computer":
        filename = "5166_Hardware_Request_Computer.pdf"
    elif type == "software":
        filename = "5165_Software_Request.pdf"
    elif type == "security_exemption":
        filename = "Request_DFO_IT_Security_Exemption.doc"

    source_file = os.path.join(settings.STATIC_DIR, "docs", "dm_tickets", filename)
    target_dir = os.path.join(settings.MEDIA_DIR, "dm_tickets", "ticket_{}".format(ticket))
    target_file = os.path.join(target_dir, filename)

    # create the new folder
    try:
        os.mkdir(target_dir)
    except:
        print("folder already exists")

    copyfile(source_file, target_file)

    my_new_file = models.File.objects.create(
        caption="unsigned {} request form".format(type),
        ticket_id=ticket,
        date_created=timezone.now(),
        file="dm_tickets/ticket_{}/{}".format(ticket, filename)
    )

    return HttpResponseRedirect(reverse('tickets:detail', kwargs={'pk': ticket}))



# Follow ups #
##############

class FollowUpCreateView(LoginRequiredMixin, CreateView):
    model = models.FollowUp
    # fields = '__all__'
    template_name = 'dm_tickets/followup_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.FollowUpForm

    def get_initial(self):
        ticket = models.Ticket.objects.get(pk=self.kwargs['ticket'])
        return {
            'ticket': ticket,
            'created_by': self.request.user.id,
            'created_date': timezone.now()
        }

    def form_valid(self, form):
        self.object = form.save()

        # create a new email object
        email = emails.NewFollowUpEmail(self.object)
        # send the email object
        if settings.PRODUCTION_SERVER:
            send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
                      recipient_list=email.to_list, fail_silently=False, )
        else:
            print('not sending email since in dev mode')
            print(email)

        return HttpResponseRedirect(reverse('tickets:close_me'))


class FollowUpUpdateView(LoginRequiredMixin, UpdateView):
    model = models.FollowUp
    template_name = 'dm_tickets/followup_form_popout.html'
    form_class = forms.FollowUpForm

    def get_initial(self):
        return {
            'created_by': self.request.user.id,
            'created_date': timezone.now()
        }

    def form_valid(self, form):
        self.object = form.save()

        # create a new email object
        email = emails.NewFollowUpEmail(self.object)
        # send the email object
        if settings.PRODUCTION_SERVER:
            send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
                      recipient_list=email.to_list, fail_silently=False, )
        else:
            print('not sending email since in dev mode')
            print(email)

        return HttpResponseRedirect(reverse('tickets:close_me'))

class FollowUpDeleteView(LoginRequiredMixin, DeleteView):
    model = models.FollowUp
    template_name = 'dm_tickets/followup_confirm_delete_popout.html'

    # form_class = forms.StudentCreateForm

    def get_success_url(self):
        return reverse_lazy('tickets:close_me')



# REPORTS #
###########

class FinanceReportListView(LoginRequiredMixin, FilterView):
    filterset_class = filters.FiscalFilter
    template_name = "dm_tickets/finance_report.html"
    queryset = models.Ticket.objects.filter(financial_follow_up_needed=True).filter(sd_ref_number__isnull=False).order_by("-date_opened")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


def finance_spreadsheet(request):
    file_url = reports.generate_finance_spreadsheet()

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="data management report for finance.xlsx"'
            return response
    raise Http404
