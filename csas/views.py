from django.shortcuts import render

from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView
from django_filters.views import FilterView

from django.urls import reverse_lazy
from . import models, forms, filters
from django.utils.translation import gettext_lazy as _


# Extend this class to add a new list view
class ListCommon(FilterView):
    # default template to use to create a filter view
    template_name = 'csas/csas_filter.html'

    # title to display on the list page
    title = None

    # key used for creating default create, update and details URLs in the get_context_data method
    # The csas/csas_list.html template expects url 'labels' to follow the format of create_[key],
    # update_[key] and details_[key]
    key = None

    # fields to be used as columns to display an object in the filter view table
    fields = []

    # URL to use to create a new object to be added to the filter view
    create_url = None

    # URL to use for the details button element in the filter view's list
    details_url = None

    # URL to use for the update button element in the filter view's list
    update_url = None

    # The height of the popup dialog used to display the creation/update form
    # if not set by the extending class the default popup height will be used
    creation_form_height = None

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, object_list=object_list, **kwargs)

        context['fields'] = self.fields

        if self.title:
            context['title'] = self.title

        context['create_url'] = self.create_url if self.create_url else "csas:create_{}".format(self.key)
        context['details_url'] = self.details_url if self.details_url else "csas:details_{}".format(self.key)
        context['update_url'] = self.update_url if self.update_url else "csas:update_{}".format(self.key)

        # When you eventually get to requiring authentication, this will be needed
        # context['auth'] = self.request.user.is_authenticated and \
        #                   self.request.user.groups.filter(name='whalesdb_admin').exists()
        context['auth'] = True

        if self.creation_form_height:
            context['height'] = self.creation_form_height

        return context


# The Create Common class is a quick way to create an entry form. define a new class that extends it
# provide a title, model and form_class and away you go.
#
# Create Common uses the _entry_form.html template to display common forms in a popup dialog intended
# to be attached to some "add new" button.
#
# class CreateCommon(UserPassesTestMixin, CreateView):
class CreateCommon(CreateView):
    # this is where the user should be redirected if they're not logged in
    login_url = '/accounts/login_required/'

    # default template to use to create an update
    template_name = 'csas/_entry_form.html'

    # title to display on the CreateView page
    title = None

    # create views are all intended to be pop out windows so upon success close the window
    success_url = reverse_lazy("csas:close_me")

    # This will be needed when you eventually get to requiring authentication
    # def test_func(self):
    #     return self.request.user.groups.filter(name='whalesdb_admin').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.title:
            context["title"] = self.title

        return context


# The Update Common class is a quick way to create an entry form to edit existing objects.
# Define a new class that extends it provide a title, model and form_class and away you go.
#
# Virtually the same as the Create Common class, the Update Common class uses the _entry_form.html
# template to display common forms in a popup dialog intended to be attached to some "update" button.
#
# class UpdateCommon(UserPassesTestMixin, UpdateView):
class UpdateCommon(UpdateView):
    # this is where the user should be redirected if they're not logged in
    login_url = '/accounts/login_required/'

    # default template to use to create an update
    template_name = 'csas/_entry_form.html'

    # title to display on the CreateView page
    title = None

    # update views are all intended to be pop out windows so upon success close the window
    success_url = reverse_lazy("csas:close_me")

    # this function overrides UserPassesTestMixin.test_func() to determine if
    # the user should have access to this content, if the user is logged in
    # def test_func(self):
    #     return self.request.user.groups.filter(name='whalesdb_admin').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.title:
            context["title"] = self.title

        return context


class DetailsCommon(DetailView):
    # default template to use to create a details view
    template_name = "csas/csas_details.html"

    # title to display on the list page
    title = None

    # key used for creating default list and update URLs in the get_context_data method
    key = None

    # URL linking the details page back to the proper list
    list_url = None
    update_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.title:
            context['title'] = self.title

        if self.fields:
            context['fields'] = self.fields

        # if you don't provide specific list and update urls by setting list_url and/or update_url
        # in the extending class, then Common Details will use the provided key to create the url for you
        context['list_url'] = self.list_url if self.list_url else "csas:list_{}".format(self.key)
        context['update_url'] = self.update_url if self.update_url else "csas:update_{}".format(self.key)

        return context


class CloserTemplateView(TemplateView):
    template_name = 'whalesdb/close_me.html'


# Create your views here.
class IndexTemplateView(TemplateView):
    template_name = 'csas/index.html'


# ################################################################################# #
# Use these contact forms as examples for creating other Entry forms                #
#                                                                                   #
# All you have to do to create new entry forms is extend                            #
# the appropriate xxxCommon class, provide the few necessary fields                 #
# ################################################################################# #
class ContactsEntry(CreateCommon):
    template_name = 'csas/_entry_form_with_nav.html'
    # The title to use on the Creation form
    title = _("New Contact Entry")
    # The model Django uses to retrieve the object(s) used on the page
    model = models.ConContact
    # This is what controls what fields and what widgets for what fields should be used on the entry form
    form_class = forms.ContactForm


class ContactsUpdate(UpdateCommon):
    # The title to use on the Update form
    title = _("Update Contact")
    # The model Django uses to retrieve the object(s) used on the page
    model = models.ConContact
    # This is what controls what fields and what widgets for what fields should be used on the entry form
    form_class = forms.ContactForm


class ContactsList(ListCommon):
    # key used to create default urls. Without it you'll need to specify a create_url, details_url and update_url
    key = 'con'
    # The model Django uses to retrieve the object(s) used on the page
    model = models.ConContact
    # filter class used to filter the table. This is where you make changes to specify what fields to filter
    # on and how those fields should be laid out or work, like inclusive vs. partial text searching
    filterset_class = filters.ContactFilter
    # fields used in the table on the filter page.
    fields = ['last_name', 'first_name', 'affiliation', 'language', 'contact_type']
    # title to display on the Filter page
    title = _("Contact List")


class ContactDetails(DetailsCommon):
    # key used to create default urls. Without it you'll need to specify a list_url and update_url
    key = "con"
    # model Django uses to get the object being displayed on the details page
    model = models.ConContact
    # title to be displayed on the details page
    title = _("Contact Details")
    # fields to be displayed on the details page
    fields = ['honorific', 'first_name', 'last_name', 'affiliation', 'job_title', 'language', 'contact_type',
              'notification_preference', 'phone', 'email', 'region', 'section', 'role', 'expertise', 'cc_grad', 'notes']

# #################################################### #
#               End of Contact Examples                #
# #################################################### #


class MeetingEntry(CreateCommon):
    # The title to use on the Creation form
    title = _("Meeting Entry")
    # The model Django uses to retrieve the object(s) used on the page
    model = models.MetMeeting
    # This is what controls what fields and what widgets for what fields should be used on the entry form
    form_class = forms.MeetingForm


class MeetingUpdate(UpdateCommon):
    # The title to use on the Update form
    title = _("Update Meeting")
    # The model Django uses to retrieve the object(s) used on the page
    model = models.MetMeeting
    # This is what controls what fields and what widgets for what fields should be used on the entry form
    form_class = forms.MeetingForm


class MeetingList(ListCommon):
    # key used to create default urls. Without it you'll need to specify a create_url, details_url and update_url
    key = 'met'
    # The model Django uses to retrieve the object(s) used on the page
    model = models.MetMeeting
    # filter class used to filter the table. This is where you make changes to specify what fields to filter
    # on and how those fields should be laid out or work, like inclusive vs. partial text searching
    filterset_class = filters.MeetingFilter
    # fields used in the table on the filter page.
    fields = ['start_date', 'title_en', 'title_fr', 'location', 'process_type']
    # title to display on the Filter page
    title = _("Meeting List")


class MeetingDetails(DetailsCommon):
    # key used to create default urls. Without it you'll need to specify a list_url and update_url
    key = "met"
    # model Django uses to get the object being displayed on the details page
    model = models.MetMeeting
    # title to be displayed on the details page
    title = _("Meeting Details")
    # fields to be displayed on the details page
    # fields = ['quarter', 'start_date', 'end_date', 'title_en', 'title_fr', 'scope', 'status', 'chair_comments',
    #           'status_notes', 'location', 'lead_region', 'other_region', 'process_type', 'program_contact',
    #           'csas_contact', ]
    fields = ['start_date', 'end_date', 'title_en', 'title_fr', 'scope', 'status', 'chair_comments',
              'status_notes', 'location', 'lead_region', 'other_region', 'process_type', 'program_contact',
              'csas_contact', ]


# #################################################### #
#               End of Meeting Examples                #
# #################################################### #


class RequestEntry(CreateCommon):
    template_name = 'csas/_entry_form_with_nav.html'
    # The title to use on the Creation form
    title = _("New Request Entry")
    # The model Django uses to retrieve the object(s) used on the page
    # model = models.MetMeeting
    model = models.ReqRequest
    # This is what controls what fields and what widgets for what fields should be used on the entry form
    # form_class = forms.MeetingForm
    form_class = forms.RequestForm


class RequestUpdate(UpdateCommon):
    # The title to use on the Update form
    title = _("Update Request")
    # The model Django uses to retrieve the object(s) used on the page
    # model = models.MetMeeting
    model = models.ReqRequest
    # This is what controls what fields and what widgets for what fields should be used on the entry form
    # form_class = forms.MeetingForm
    form_class = forms.RequestForm


class RequestList(ListCommon):
    # key used to create default urls. Without it you'll need to specify a create_url, details_url and update_url
    # key = 'met'
    key = 'req'
    # The model Django uses to retrieve the object(s) used on the page
    # model = models.MetMeeting
    model = models.ReqRequest
    # filter class used to filter the table. This is where you make changes to specify what fields to filter
    # on and how those fields should be laid out or work, like inclusive vs. partial text searching
    # filterset_class = filters.MeetingFilter
    filterset_class = filters.RequestFilter
    # fields used in the table on the filter page.
    # fields = ['start_date', 'title_en', 'title_fr', 'location', 'process_type']
    fields = ['region', 'title', 'client_name', 'have_funding']
    # title to display on the Filter page
    # title = _("Meeting List")
    title = _("Request List")


class RequestDetails(DetailsCommon):
    # key used to create default urls. Without it you'll need to specify a list_url and update_url
    # key = "met"
    key = "req"
    # model Django uses to get the object being displayed on the details page
    # model = models.MetMeeting
    model = models.ReqRequest
    # title to be displayed on the details page
    # title = _("Meeting Details")
    title = _("Request Details")
    # fields to be displayed on the details page
    #fields = ['quarter', 'start_date', 'end_date', 'title_en', 'title_fr', 'scope', 'status', 'chair_comments',
    #          'status_notes', 'location', 'lead_region', 'other_region', 'process_type', 'program_contact',
    #          'csas_contact', ]
    fields = ['title', 'in_year_request', 'region', 'client_sector', 'client_name', 'client_title', 'client_email',
              'issue', 'priority', 'rationale', 'proposed_timing', 'rational_for_timing', 'have_funding',
              'funding_notes', 'science_discussion', 'science_discussion_notes', 'decision', 'decision_explanation',
              'advisor_submission', 'rd_submission', 'decision_date', ]


# class MeetingsTemplateView(CreateView):
#     template_name = 'csas/meetings.html'
#     model = models.MetMeeting
#     form_class = forms.MeetingForm


# class PublicationsTemplateView(CreateView):
#     template_name = 'csas/publications.html'
#     model = models.PubPublication
#     form_class = forms.PublicationForm


# class RequestsTemplateView(CreateView):
#     template_name = 'csas/requests.html'
#     model = models.MetMeeting
#     form_class = forms.MeetingForm


# class OthersTemplateView(CreateView):
#     template_name = 'csas/others.html'
#     model = models.MetMeeting
#     form_class = forms.MeetingForm


class CommonLookup(CreateView):
    template_name = 'csas/_lookup_entry_form.html'
    fields = ['name']
    success_url = reverse_lazy("csas:close_me")


class HonorificView(CommonLookup):
    model = models.CohHonorific


class LanguageView(CommonLookup):
    model = models.LanLanguage
