import json
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import TextField
from django.db.models.functions import Concat
from django.utils import timezone
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, ListView, TemplateView
###

from lib.functions.nz import nz
from . import models
from . import forms
from . import emails


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'travel/close_me.html'


def in_travel_admin_group(user):
    if user:
        return user.groups.filter(name='travel_admin').count() != 0


class TravelAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_travel_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


# This allows any logged in user to access the view
class TravelAccessRequiredMixin(LoginRequiredMixin):
    login_url = '/accounts/login_required/'


class IndexTemplateView(TravelAccessRequiredMixin, TemplateView):
    template_name = 'travel/index.html'


# SERVER #
##########
class EventListView(TravelAccessRequiredMixin, ListView):
    model = models.Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Event.objects.first()
        context["field_list"] = [
            'section',
            'first_name',
            'last_name',
            'trip_title',
            'location',
            'conf_start_date',
            'conf_end_date',
            'plan_number',
            'total_cost',
        ]
        return context


class EventDetailView(TravelAccessRequiredMixin, DetailView):
    model = models.Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'user',
            'section',
            'first_name',
            'last_name',
            'address',
            'phone',
            'email',
            'public_servant',
            'company_name',
            'trip_title',
            'location',
            'conf_start_date',
            'conf_end_date',
            'plan_number',

            # purpose
            'role',
            'reason',
            'purpose',
            'role_of_participant',
            'objective_of_event',
            'benefit_to_dfo',
            'multiple_conferences_rationale',
            'multiple_attendee_rationale',

            # costs
            'air',
            'rail',
            'rental_motor_vehicle',
            'personal_motor_vehicle',
            'taxi',
            'other_transport',
            'accommodations',
            'meals',
            'incidentals',
            'other',
            'total_cost',
            'cost_breakdown|{}'.format(_("cost summary")),
            'purpose_long|{}'.format(_("purpose")),
        ]
        return context


class EventUpdateView(TravelAccessRequiredMixin, UpdateView):
    model = models.Event
    form_class = forms.EventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_dict = {}
        for user in User.objects.all():
            user_dict[user.id] = {}
            user_dict[user.id]['first_name'] = user.first_name
            user_dict[user.id]['last_name'] = user.last_name
            user_dict[user.id]['email'] = user.email

        user_json = json.dumps(user_dict)
        # send JSON file to template so that it can be used by js script
        context['user_json'] = user_json
        return context


class EventCreateView(TravelAccessRequiredMixin, CreateView):
    model = models.Event
    form_class = forms.EventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_dict = {}
        for user in User.objects.all():
            user_dict[user.id] = {}
            user_dict[user.id]['first_name'] = user.first_name
            user_dict[user.id]['last_name'] = user.last_name
            user_dict[user.id]['email'] = user.email

        user_json = json.dumps(user_dict)
        # send JSON file to template so that it can be used by js script
        context['user_json'] = user_json
        return context


class EventDeleteView(TravelAccessRequiredMixin, DeleteView):
    model = models.Event
    success_url = reverse_lazy('travel:event_list')
    success_message = 'The event was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# # USER #
# ##########
# class UserListView(travelAdminRequiredMixin, ListView):
#     model = models.User
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["my_object"] = models.User.objects.first()
#         context["field_list"] = [
#             'server',
#             'username',
#             'travel',
#             'status',
#         ]
#         return context
#
#
# class UserDetailView(travelAdminRequiredMixin, DetailView):
#     model = models.User
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["field_list"] = [
#             'username',
#             'password',
#             'server',
#             'notes',
#             'status',
#         ]
#         return context
#
#
# class UserUpdateView(travelAdminRequiredMixin, UpdateView):
#     model = models.User
#     form_class = forms.UserForm
#
#
# class UserCreateView(travelAdminRequiredMixin, CreateView):
#     model = models.User
#     form_class = forms.UserForm
#
#
# class UserCreateViewPopout(travelAdminRequiredMixin, CreateView):
#     model = models.User
#     form_class = forms.UserForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('travel:close_me'))
#
#
# class UserDeleteView(travelAdminRequiredMixin, DeleteView):
#     model = models.User
#     success_url = reverse_lazy('travel:event_list')
#     success_message = 'The user was deleted successfully!'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
#
#
# def send_instructions(request, pk):
#     # create a new email object
#     my_user = models.User.objects.get(pk=pk)
#     email = emails.SendInstructionsEmail(my_user)
#     # send the email object
#     if settings.MY_ENVR != 'dev':
#         send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
#                   recipient_list=email.to_list, fail_silently=False, )
#     else:
#         print('not sending email since in dev mode')
#         print("from={}".format(email.from_email))
#         print("to={}".format(email.to_list))
#         print("subject={}".format(email.subject))
#         print("message={}".format(email.message))
#
#     messages.success(request, "An email has been sent to the user with setup instructions!")
#
#     return HttpResponseRedirect(reverse("travel:user_detail", kwargs={"pk": pk}))
#
#
# # SHARE #
# #########
# class ShareListView(travelAdminRequiredMixin, ListView):
#     model = models.Share
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["my_object"] = models.Share.objects.first()
#         context["field_list"] = [
#             'server',
#             'name',
#             'local_path',
#             'mounted_path',
#             'network_path',
#         ]
#         return context
#
#
# class ShareDetailView(travelAdminRequiredMixin, DetailView):
#     model = models.Share
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["field_list"] = [
#             'server',
#             'name',
#             'local_path',
#             'mounted_path',
#             'network_path',
#             'notes',
#         ]
#         return context
#
#
# class ShareUpdateView(travelAdminRequiredMixin, UpdateView):
#     model = models.Share
#     form_class = forms.ShareForm
#
#
# class ShareCreateView(travelAdminRequiredMixin, CreateView):
#     model = models.Share
#     form_class = forms.ShareForm
#
#
# class ShareCreateViewPopout(travelAdminRequiredMixin, CreateView):
#     model = models.Share
#     form_class = forms.ShareForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('travel:close_me'))
#
#
# class ShareDeleteView(travelAdminRequiredMixin, DeleteView):
#     model = models.Share
#     success_url = reverse_lazy('travel:event_list')
#     success_message = 'The share was deleted successfully!'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
