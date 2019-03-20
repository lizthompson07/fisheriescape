from django.core.files import File
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, UpdateView, DeleteView, CreateView, DetailView, ListView
from django_filters.views import FilterView

from shutil import copyfile
import json
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
            search_term=Concat('title', 'description', 'notes', output_field=TextField()))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["my_object"] = models.Ticket.objects.first()
        context["field_list"] = [
            'id',
            'date_modified',
            'section',
            'title',
            'request_type',
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

class TicketDetailView(DetailView):
    model = models.Ticket
    template_name = "dm_tickets/ticket_detail.html"
    # form_class = forms.TicketDetailForm

    def get_context_data(self, **kwargs):
        context = super(TicketDetailView, self).get_context_data(**kwargs)

        try:
            extra_context = {'temp_msg':self.request.session['temp_msg']}
            context.update(extra_context)
            del self.request.session['temp_msg']
        except Exception as e:
            print("type error: " + str(e))
            # pass
        context['email'] = emails.TicketResolvedEmail(self.object)
        context["field_group_1"] = [
                # "id",
                "primary_contact",
                "title",
                "section",
                "status",
                "priority",
                "request_type",
            ]

        context["field_group_2"] = [
            "financial_coding",
            "description",
            "notes_html",
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
    if settings.MY_ENVR != 'dev':
        send_mail( message='', subject=email.subject, html_message=email.message, from_email=email.from_email, recipient_list=email.to_list,fail_silently=False,)
    else:
        print('not sending email since in dev mode')
    my_ticket.resolved_email_date = timezone.now()
    my_ticket.save()
    messages.success(request, "the email has been sent!")
    return HttpResponseRedirect(reverse('tickets:detail', kwargs={'pk':ticket}))

def mark_ticket_resolved(request, ticket):
    my_ticket = models.Ticket.objects.get(pk=ticket)
    my_ticket.status = '2'
    my_ticket.save()
    return HttpResponseRedirect(reverse('tickets:detail', kwargs={'pk':ticket}))

def mark_ticket_active(request, ticket):
    my_ticket = models.Ticket.objects.get(pk=ticket)
    my_ticket.status = "5"
    my_ticket.date_closed = None
    my_ticket.save()
    return HttpResponseRedirect(reverse('tickets:detail', kwargs={'pk':ticket}))



class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Ticket
    template_name = "dm_tickets/ticket_form.html"
    login_url = '/accounts/login_required/'
    form_class = forms.TicketForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # produce a dictionary of people
        email_dict = {}
        for person in models.Person.objects.all():
            email_dict[person.id] = person.email
        # convert dict to JSON
        email_json = json.dumps(email_dict)
        # send JSON file to template so that it can be used by js script
        context['email_json'] = email_json
        return context

    def form_valid(self, form):
        self.object = form.save()
        self.object.primary_contact.email = form.cleaned_data["primary_contact_email"]
        self.object.primary_contact.save()
        return HttpResponseRedirect(self.get_success_url())

class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Ticket
    success_url = reverse_lazy('tickets:list')
    login_url = '/accounts/login_required/'

class TicketCreateView(CreateView):
    model = models.Ticket
    login_url = '/accounts/login_required/'
    form_class = forms.TicketForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # produce a dictionary of people
        email_dict = {}
        for person in models.Person.objects.all():
            email_dict[person.id] = person.email
        # convert dict to JSON
        email_json = json.dumps(email_dict)
        # send JSON file to template so that it can be used by js script
        context['email_json'] = email_json
        return context

    def form_valid(self, form):
        self.object = form.save()
        # do something with self.object #
        #################################
        self.object.people.add(self.object.primary_contact)
        # update the primary contact email with the form data
        self.object.primary_contact.email = form.cleaned_data["primary_contact_email"]
        self.object.primary_contact.save()

        # create a new email object
        email = emails.NewTicketEmail(self.object)
        # send the email object
        if settings.MY_ENVR != 'dev':
            send_mail( message='', subject=email.subject, html_message=email.message, from_email=email.from_email, recipient_list=email.to_list,fail_silently=False,)
        else:
            print('not sending email since in dev mode')

        messages.success(self.request, "The new ticket has been logged and a confirmation email has been sent!")


        # check to see if a generic file should be appended
        if form.cleaned_data["generic_file_to_load"]:
            return HttpResponseRedirect(reverse_lazy("tickets:add_generic_file", kwargs={"ticket":self.object.id, "type":form.cleaned_data["generic_file_to_load"]}))

        # if nothing, just go to detail page
        else:
            return HttpResponseRedirect(self.get_success_url())

class TicketNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Ticket
    template_name = "dm_tickets/ticket_note_form.html"
    login_url = '/accounts/login_required/'
    form_class = forms.TicketNoteForm



# Tags #
########

class TagDetailView(UpdateView):
    model = models.Tag
    template_name ='dm_tickets/tag_detail_popout.html'
    form_class = forms.TagForm

class TagUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Tag
    template_name ='dm_tickets/tag_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.TagForm

class TagCreateView(CreateView):
    model = models.Tag
    template_name ='dm_tickets/tag_form_popout.html'
    form_class = forms.TagForm

    def form_valid(self, form):
        self.object = form.save()
        ticket = self.kwargs['ticket']
        return HttpResponseRedirect(reverse_lazy('tickets:add_tag', kwargs={'ticket':ticket, 'tag':self.object.id}))

class TagListView(FilterView):
    filterset_class = filters.TagFilter
    template_name = "dm_tickets/tag_insert_list.html"

    def get_context_data(self, **kwargs):
        context = super(TagListView, self).get_context_data(**kwargs)
        ticket = self.kwargs['ticket']
        context['ticket']= ticket
        return context

def add_tag_to_ticket(request, ticket, tag):
    my_ticket = models.Ticket.objects.get(id=ticket)
    my_ticket.tags.add(tag)
    return HttpResponseRedirect(reverse('tickets:tag_insert', kwargs={'ticket':ticket}))

# Files #
#########

class FileCreateView(CreateView):
    model = models.File
    # fields = '__all__'
    template_name ='dm_tickets/file_form_popout.html'
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
        if settings.MY_ENVR != 'dev':
            send_mail( message='', subject=email.subject, html_message=email.message, from_email=email.from_email, recipient_list=email.to_list,fail_silently=False,)
        else:
            print('not sending email since in dev mode')

        #store a temporary message is the sessions middleware
        self.request.session['temp_msg'] = "The new file has been added and a notification email has been sent to the site administrator."

        # determine if we should attach a generic file

        return HttpResponseRedirect(reverse('tickets:close_me'))

class FileUpdateView(UpdateView):
    model = models.File
    fields = '__all__'
    template_name ='dm_tickets/file_form_popout.html'
    # form_class = forms.StudentCreateForm

class FileDetailView(LoginRequiredMixin,UpdateView):
    model = models.File
    fields = '__all__'
    template_name ='dm_tickets/file_detail_popout.html'
    # form_class = forms.TagForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            extra_context = {'temp_msg':self.request.session['temp_msg']}
            context.update(extra_context)
            del self.request.session['temp_msg']
        except Exception as e:
            print("type error: " + str(e))
            # pass

        return context

class FileDeleteView(LoginRequiredMixin,DeleteView):
    model = models.File
    template_name ='dm_tickets/file_confirm_delete_popout.html'
    # form_class = forms.StudentCreateForm

    def get_success_url(self):
        return reverse_lazy('tickets:close_me')


def add_generic_file(request, ticket, type):
    # if settings.MY_ENVR == "dev":
    #     print("cannot do transfer file from dev")
    # else:

    if type == "monitor":
        filename = "5166_Hardware_Request_Monitor.pdf"
    elif type == "computer":
        filename = "5166_Hardware_Request_Computer.pdf"
    elif type == "software":
        filename = "5165_Software_Request.pdf"
    elif type == "security_exemption":
        filename = "Request_DFO_IT_Security_Exemption.doc"


    source_file = os.path.join(settings.STATIC_DIR,"docs","dm_tickets",filename)
    target_dir = os.path.join(settings.MEDIA_DIR,"dm_tickets","ticket_{}".format(ticket))
    target_file= os.path.join(target_dir,filename)

    # create the new folder
    try:
        os.mkdir(target_dir)
    except:
        print("folder already exists")

    copyfile(source_file,target_file)


    my_new_file = models.File.objects.create(
        caption = "unsigned {} request form".format(type),
        ticket_id = ticket,
        date_created = timezone.now(),
        file="dm_tickets/ticket_{}/{}".format(ticket,filename)
    )

    return HttpResponseRedirect(reverse('tickets:detail', kwargs={'pk': ticket}))


# People #
##########

class PersonDetailView(UpdateView):
    model = models.Person
    template_name ='dm_tickets/person_detail_popout.html'
    fields = '__all__'

class PersonUpdateView(UpdateView):
    model = models.Person
    template_name ='dm_tickets/person_form_popout.html'
    login_url = '/accounts/login_required/'
    fields = '__all__'

class PersonCreateView(CreateView):
    model = models.Person
    template_name ='dm_tickets/person_form_popout.html'
    fields = '__all__'

    def form_valid(self, form):
        self.object = form.save()
        try:
            ticket = self.kwargs['ticket']
        except:
            return HttpResponseRedirect(reverse('tickets:close_me'))
        else:
            return HttpResponseRedirect(reverse_lazy('tickets:add_person', kwargs={'ticket':ticket, 'person':self.object.id}))


class PersonListView(FilterView):
    filterset_class = filters.PersonFilter
    template_name = "dm_tickets/person_insert_list.html"

    def get_context_data(self, **kwargs):
        context = super(PersonListView, self).get_context_data(**kwargs)
        ticket = self.kwargs['ticket']
        context['ticket']= ticket
        return context

def add_person_to_ticket(request, ticket, person):
    my_ticket = models.Ticket.objects.get(id=ticket)
    my_ticket.people.add(person)
    return HttpResponseRedirect(reverse('tickets:person_insert', kwargs={'ticket':ticket}))


# REPORTS #
###########

class FinanceReportListView(FilterView):
    filterset_class = filters.FiscalFilter
    template_name = "dm_tickets/finance_report.html"
    queryset = models.Ticket.objects.filter(financial_follow_up_needed=True).filter(sd_ref_number__isnull=False).order_by("-date_opened")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"]= timezone.now()
        return context

def finance_spreadsheet(request):
    file_url = reports.generate_finance_spreadsheet()

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="data management report for finance.xlsx"'
            return response
    raise Http404