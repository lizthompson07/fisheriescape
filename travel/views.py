import json
import os
from copy import deepcopy

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Sum, Q
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, ListView, TemplateView, FormView
###
from django_filters.views import FilterView
from easy_pdf.views import PDFTemplateView

from lib.functions.custom_functions import fiscal_year
from lib.templatetags.custom_filters import nz
from . import models
from . import forms
from . import reports
from . import emails
from . import filters

from shared_models import models as shared_models


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'travel/close_me.html'


def in_travel_admin_group(user):
    if user.id:
        return user.groups.filter(name='travel_admin').count() != 0


def is_approver(user, event):
    if user == event.recommender_1 or user == event.recommender_2 or user == event.recommender_3 or user == event.approver:
        return True


class TravelAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_travel_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class AdminOrApproverRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        my_event = models.Event.objects.get(pk=self.kwargs.get("pk"))
        my_user = self.request.user
        if in_travel_admin_group(my_user) or is_approver(my_user, my_event):
            return True

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["number_waiting"] = models.Event.objects.filter(waiting_on=self.request.user).count()
        approval_count = models.Event.objects.filter(
            Q(recommender_1=self.request.user) | Q(recommender_2=self.request.user) | Q(recommender_3=self.request.user) | Q(
                rdg=self.request.user) | Q(adm=self.request.user)).count()

        context["is_approver"] = True if approval_count > 0 else False
        print(approval_count)
        return context


event_field_list = [
    'fiscal_year',
    'status',
    'user',
    'section',
    'first_name',
    'last_name',
    'address',
    'phone',
    'email',
    'public_servant',
    'company_name',
    'region',
    'trip_title',
    'departure_location',
    'destination',
    'start_date',
    'end_date',
    'event',
    'registered_event',

    # purpose
    'role',
    'reason',
    'purpose',
    'role_of_participant',
    'objective_of_event',
    'benefit_to_dfo',
    'multiple_conferences_rationale',
    'multiple_attendee_rationale',
    'late_justification',
    'bta_attendees',
    'notes',

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
    'registration',
    'other',
    'total_cost',
    'cost_breakdown|{}'.format(_("cost summary")),
    'purpose_long|{}'.format(_("purpose")),

    # costs
    'recommender_1_status|{}'.format(_("Recommender 1")),
    'recommender_2_status|{}'.format(_("Recommender 2")),
    'recommender_3_status|{}'.format(_("Recommender 3")),
    'adm_status|{}'.format(_("ADM")),
    'rdg_status|{}'.format(_("Expenditure Initiation (RDG)")),
]

event_group_field_list = [
    'fiscal_year',
    'status',
    'user',
    'section',
    'trip_title',
    'destination',
    'start_date',
    'end_date',
    'event',
    'registered_event',

    'reason',
    'purpose',
    'objective_of_event',
    'benefit_to_dfo',
    'multiple_attendee_rationale',
    'funding_source',
    'bta_attendees',
    'late_justification',
    'notes',
    'total_trip_cost|{}'.format(_("Total trip cost")),

    'recommender_1_status|{}'.format(_("Recommender 1")),
    'recommender_2_status|{}'.format(_("Recommender 2")),
    'recommender_3_status|{}'.format(_("Recommender 3")),
    'adm_status|{}'.format(_("ADM")),
    'rdg_status|{}'.format(_("Expenditure Initiation (RDG)")),
]

event_child_field_list = [
    'first_name',
    'last_name',
    # 'address',
    # 'phone',
    # 'email',
    'public_servant',
    'region',

    # 'company_name',
    'departure_location',
    'role',
    'role_of_participant',
    # 'reason',
    # 'purpose_long|{}'.format(_("purpose")),
    # 'cost_breakdown|{}'.format(_("cost summary")),
    'total_cost',
]


# EVENT #
#########
class EventListView(TravelAccessRequiredMixin, FilterView):
    queryset = models.Event.objects.filter(parent_event__isnull=True)
    filterset_class = filters.EventFilter
    template_name = 'travel/event_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Event.objects.first()
        context["field_list"] = [
            'fiscal_year',
            'is_group_trip',
            'status',
            'section',
            'first_name',
            'last_name',
            'trip_title',
            'destination',
            'start_date',
            'end_date',
            'total_trip_cost|{}'.format(_("Total trip cost")),

        ]
        return context


class EventApprovalListView(TravelAccessRequiredMixin, ListView):
    model = models.Event
    template_name = 'travel/event_approval_list.html'

    def get_queryset(self):
        qs = models.Event.objects.filter(parent_event__isnull=True).filter(
            Q(recommender_1=self.request.user) | Q(recommender_2=self.request.user) | Q(recommender_3=self.request.user) | Q(
                adm=self.request.user) | Q(rdg=self.request.user)).order_by("-submitted")
        return qs.filter(waiting_on=self.request.user) if self.kwargs.get("which_ones") == "awaiting" else qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Event.objects.first()
        context["awaiting"] = True if self.kwargs.get("which_ones") else False
        context["field_list"] = [
            'is_group_trip',
            'first_name',
            'last_name',
            'trip_title',
            'destination',
            'start_date',
            'end_date',
            'total_trip_cost|{}'.format(_("Total trip cost")),
            'recommender_1_status|{}'.format(_("Recommender 1<br>(status)")),
            'recommender_2_status|{}'.format(_("Recommender 2<br>(status)")),
            'recommender_3_status|{}'.format(_("Recommender 3<br>(status)")),
            'adm_status|{}'.format(_("ADM<br>(status)")),
            'rdg_status|{}'.format(_("RDG<br>(status)")),
        ]
        return context


class EventAdminApprovalListView(TravelAdminRequiredMixin, ListView):
    model = models.Event
    template_name = 'travel/event_approval_list.html'

    def get_queryset(self):
        # return a list only of those awaiting ADM or RDG approval
        qs = models.Event.objects.filter(
            parent_event__isnull=True,
        ).filter(Q(status_id=14) | Q(status_id=15)).order_by("-submitted")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Event.objects.first()
        context["admin"] = True
        context["field_list"] = [
            'is_group_trip',
            'first_name',
            'last_name',
            'trip_title',
            'destination',
            'start_date',
            'end_date',
            'total_trip_cost|{}'.format(_("Total trip cost")),
            'recommender_1_status|{}'.format(_("Recommender 1<br>(status)")),
            'recommender_2_status|{}'.format(_("Recommender 2<br>(status)")),
            'recommender_3_status|{}'.format(_("Recommender 3<br>(status)")),
            'adm_status|{}'.format(_("ADM<br>(status)")),
            'rdg_status|{}'.format(_("RDG<br>(status)")),
        ]
        return context


class EventDetailView(TravelAccessRequiredMixin, DetailView):
    model = models.Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = self.get_object()
        context["field_list"] = event_field_list if not my_object.is_group_trip else event_group_field_list
        my_event_child_field_list = deepcopy(event_child_field_list)
        if not my_object.event:
            my_event_child_field_list.remove("role")
            my_event_child_field_list.remove("role_of_participant")
        context["child_field_list"] = my_event_child_field_list
        context["is_admin"] = "travel_admin" in [group.name for group in self.request.user.groups.all()]
        context["is_owner"] = my_object.user == self.request.user

        return context


class EventUpdateView(TravelAccessRequiredMixin, UpdateView):
    model = models.Event

    def get_template_names(self):
        return 'travel/event_form_popout.html' if self.kwargs.get("pop") else 'travel/event_form.html'

    def get_form_class(self):
        return forms.ChildEventForm if self.kwargs.get("pop") else forms.EventForm

    def form_valid(self, form):
        my_object = form.save()
        if not my_object.parent_event:
            if form.cleaned_data.get("stay_on_page"):
                return HttpResponseRedirect(reverse_lazy("travel:event_edit", kwargs={"pk": my_object.id}))
            else:
                return HttpResponseRedirect(reverse_lazy("travel:event_detail", kwargs={"pk": my_object.id}))
        else:
            return HttpResponseRedirect(reverse("shared_models:close_me"))

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

        # need to create a dictionary for sections and who the recommenders / appovers are
        section_dict = {}
        for section in shared_models.Section.objects.all():
            section_dict[section.id] = {}
            section_dict[section.id]["recommender_1"] = section.head_id
            section_dict[section.id]["recommender_2"] = section.division.head_id
            section_dict[section.id]["recommender_3"] = section.division.branch.head_id
            section_dict[section.id]["rdg"] = section.division.branch.region.head_id
            section_dict[section.id]["adm"] = User.objects.get(email__iexact="Arran.McPherson@dfo-mpo.gc.ca").id
        section_json = json.dumps(section_dict)
        # send JSON file to template so that it can be used by js script
        context['section_json'] = section_json

        return context


class EventApproveUpdateView(AdminOrApproverRequiredMixin, FormView):
    model = models.Event
    form_class = forms.EventApprovalForm
    template_name = 'travel/event_approval_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = models.Event.objects.get(pk=self.kwargs.get("pk"))
        context["object"] = my_object
        context["field_list"] = event_field_list if not my_object.is_group_trip else event_group_field_list
        context["child_field_list"] = event_child_field_list

        return context

    def form_valid(self, form):
        is_approved = form.cleaned_data.get("is_approved")
        my_event = models.Event.objects.get(pk=self.kwargs.get("pk"))
        # if the user approved the project, we should approve anything that is them
        if my_event.recommender_1 == self.request.user:
            my_event.recommender_1_approval_date = timezone.now()
            if is_approved:
                my_event.recommender_1_approval_status_id = 2
            else:
                my_event.recommender_1_approval_status_id = 3
                my_event.recommender_2_approval_status_id = 5
                my_event.recommender_3_approval_status_id = 5
                my_event.adm_approval_status_id = 5
                my_event.rdg_approval_status_id = 5

        if my_event.recommender_2 == self.request.user:
            my_event.recommender_2_approval_date = timezone.now()
            if is_approved:
                my_event.recommender_2_approval_status_id = 2
            else:
                my_event.recommender_2_approval_status_id = 3
                my_event.recommender_3_approval_status_id = 5
                my_event.adm_approval_status_id = 5
                my_event.rdg_approval_status_id = 5

        if my_event.recommender_3 == self.request.user:
            my_event.recommender_3_approval_date = timezone.now()
            if is_approved:
                my_event.recommender_3_approval_status_id = 2
            else:
                my_event.recommender_3_approval_status_id = 3
                my_event.adm_approval_status_id = 5
                my_event.rdg_approval_status_id = 5

        if my_event.adm == self.request.user:
            my_event.adm_approval_date = timezone.now()
            if is_approved:
                my_event.adm_approval_status_id = 2
            else:
                my_event.adm_approval_status_id = 3
                my_event.rdg_approval_status_id = 5

        if my_event.rdg == self.request.user:
            my_event.rdg_approval_date = timezone.now()
            if is_approved:
                my_event.rdg_approval_status_id = 2
            else:
                my_event.rdg_approval_status_id = 3

        my_event.save()
        return HttpResponseRedirect(reverse("travel:event_approval_list"))


class EventAdminApproveUpdateView(TravelAdminRequiredMixin, UpdateView):
    model = models.Event
    form_class = forms.AdminEventForm
    template_name = 'travel/event_approval_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = self.get_object()
        context["admin"] = True
        context["object"] = my_object

        return context

    def form_valid(self, form):
        my_event = form.save(commit=False)

        # if approval status is not pending, we add a date stamp
        if my_event.adm_approval_status_id != 1:
            my_event.adm_approval_date = timezone.now()

        if my_event.rdg_approval_status_id != 1:
            my_event.rdg_approval_date = timezone.now()

        # if denied by adm, rdg will be canceled
        if my_event.adm_approval_status_id == 3:
            my_event.rdg_approval_status_id = 5

        # Now do a full save
        my_event.save()
        return HttpResponseRedirect(reverse("travel:admin_approval_list"))


class EventSubmitUpdateView(TravelAccessRequiredMixin, FormView):
    model = models.Event
    form_class = forms.EventApprovalForm
    template_name = 'travel/event_submission_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = models.Event.objects.get(pk=self.kwargs.get("pk"))
        context["object"] = my_object
        context["field_list"] = event_field_list if not my_object.is_group_trip else event_group_field_list
        context["child_field_list"] = event_child_field_list

        return context

    def form_valid(self, form):
        my_event = models.Event.objects.get(pk=self.kwargs.get("pk"))
        # figure out the current state of the trip
        is_submitted = True if my_event.submitted else False

        # if submitted, then unsumbit but only if admin
        if is_submitted:
            if in_travel_admin_group(self.request.user) or my_event.user == self.request.user:
                my_event.submitted = None
            else:
                messages.error(self.request, "sorry, only admins or owners can unsubmit trips")
        else:
            my_event.submitted = timezone.now()
        my_event.save()
        return HttpResponseRedirect(reverse("travel:event_detail", kwargs={"pk": my_event.id}))


class EventCreateView(TravelAccessRequiredMixin, CreateView):
    model = models.Event

    def get_template_names(self):
        my_object = models.Event.objects.get(pk=self.kwargs.get("pk")) if self.kwargs.get("pk") else None
        return 'travel/event_form_popout.html' if my_object else 'travel/event_form.html'

    def get_form_class(self):
        my_object = models.Event.objects.get(pk=self.kwargs.get("pk")) if self.kwargs.get("pk") else None
        return forms.ChildEventForm if my_object else forms.EventForm

    def get_initial(self):
        my_object = models.Event.objects.get(pk=self.kwargs.get("pk")) if self.kwargs.get("pk") else None
        return {"user": self.request.user} if not my_object else {"parent_event": my_object}

    def form_valid(self, form):
        my_object = form.save()

        # if it is a group trip, add the main user as a traveller
        if my_object.is_group_trip:
            models.Event.objects.create(
                user=self.request.user,
                first_name=self.request.user.first_name,
                last_name=self.request.user.last_name,
                email=self.request.user.email,
                parent_event=my_object,
            )

        if not my_object.parent_event:
            if form.cleaned_data.get("stay_on_page"):
                return HttpResponseRedirect(reverse_lazy("travel:event_edit", kwargs={"pk": my_object.id}))
            else:
                return HttpResponseRedirect(reverse_lazy("travel:event_detail", kwargs={"pk": my_object.id}))
        else:
            return HttpResponseRedirect(reverse("shared_models:close_me"))

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

        # need to create a dictionary for sections and who the recommenders / appovers are
        section_dict = {}
        for section in shared_models.Section.objects.all():
            section_dict[section.id] = {}
            section_dict[section.id]["recommender_1"] = section.head_id
            section_dict[section.id]["recommender_2"] = section.division.head_id
            section_dict[section.id]["recommender_3"] = section.division.branch.head_id
            section_dict[section.id]["rdg"] = section.division.branch.region.head_id
            section_dict[section.id]["adm"] = User.objects.get(email__iexact="Arran.McPherson@dfo-mpo.gc.ca").id
        section_json = json.dumps(section_dict)
        # send JSON file to template so that it can be used by js script
        context['section_json'] = section_json
        return context


class EventDeleteView(TravelAccessRequiredMixin, DeleteView):
    model = models.Event
    success_message = 'The event was deleted successfully!'

    def get_template_names(self):
        if self.kwargs.get('pop'):
            template_name = 'travel/event_confirm_delete_popout.html'
        else:
            template_name = 'travel/event_confirm_delete.html'
        return template_name

    def get_success_url(self):
        if self.kwargs.get('pop'):
            success_url = reverse('shared_models:close_me')
        else:
            success_url = reverse_lazy('travel:event_list')
        return success_url

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class EventCloneUpdateView(EventUpdateView):
    def test_func(self):
        if self.request.user.id:
            return True

    def get_initial(self):
        my_object = models.Event.objects.get(pk=self.kwargs["pk"])
        init = super().get_initial()
        init["trip_title"] = "DUPLICATE OF: {}".format(my_object.trip_title)
        init["year"] = fiscal_year(sap_style=True, next=True)
        # init["created_by"] = self.request.user
        return init

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cloned"] = True
        return context

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        old_obj = models.Event.objects.get(pk=new_obj.pk)
        new_obj.pk = None
        new_obj.submitted = None
        new_obj.save()
        return HttpResponseRedirect(reverse_lazy("travel:event_detail", kwargs={"pk": new_obj.id}))



class ChildEventCloneUpdateView(EventCreateView):
    def test_func(self):
        if self.request.user.id:
            return True

    def get_initial(self):
        my_object = models.Event.objects.get(pk=self.kwargs["pk"])
        init = super().get_initial()
        init["parent_event"] = my_object.parent_event
        init["departure_location"] = my_object.departure_location
        init["role"] = my_object.role
        init["role_of_participant"] = my_object.role_of_participant
        init["air"] = my_object.air
        init["rail"] = my_object.rail
        init["rental_motor_vehicle"] = my_object.rental_motor_vehicle
        init["personal_motor_vehicle"] = my_object.personal_motor_vehicle
        init["taxi"] = my_object.taxi
        init["other_transport"] = my_object.other_transport
        init["meals"] = my_object.meals
        init["accommodations"] = my_object.accommodations
        init["incidentals"] = my_object.incidentals
        init["registration"] = my_object.registration
        init["other"] = my_object.other
        return init

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cloned"] = True
        return context

    # def form_valid(self, form):
    #     new_obj = form.save()
    #     return HttpResponseRedirect(reverse_lazy("travel:event_detail", kwargs={"pk": new_obj.id}))



# REGISTERED EVENT #
####################

class RegisteredEventListView(TravelAccessRequiredMixin, FilterView):
    model = models.RegisteredEvent
    filterset_class = filters.RegisteredEventFilter
    template_name = 'travel/registeredevent_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.RegisteredEvent.objects.first()
        context["field_list"] = [
            'name',
            'nom',
            'number',
            'start_date',
            'end_date',
        ]
        return context


class RegisteredEventDetailView(TravelAccessRequiredMixin, DetailView):
    model = models.RegisteredEvent

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name',
            'nom',
            'number',
            'start_date',
            'end_date',
        ]
        return context


class RegisteredEventUpdateView(TravelAccessRequiredMixin, UpdateView):
    model = models.RegisteredEvent
    form_class = forms.RegisteredEventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RegisteredEventCreateView(TravelAccessRequiredMixin, CreateView):
    model = models.RegisteredEvent
    form_class = forms.RegisteredEventForm

    def get_template_names(self):
        if self.kwargs.get("pop"):
            return 'travel/registeredevent_form_popout.html'
        else:
            return 'travel/event_form.html'

    def get_success_url(self):
        if self.kwargs.get("pop"):
            return reverse("shared_models:close_me")
        else:
            return super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        my_object = form.save()
        if self.kwargs.get("pop"):
            # create a new email object
            email = emails.NewEventEmail(my_object)
            # send the email object
            if settings.PRODUCTION_SERVER:
                send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
                          recipient_list=email.to_list, fail_silently=False, )
            else:
                print(email)
            messages.success(self.request,
                             _("The event has been added to the database!"))
        return super().form_valid(form)


class RegisteredEventDeleteView(TravelAccessRequiredMixin, DeleteView):
    model = models.RegisteredEvent
    success_url = reverse_lazy('travel:revent_list')
    success_message = 'The event was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# REPORTS #
###########

class ReportSearchFormView(TravelAccessRequiredMixin, FormView):
    template_name = 'travel/report_search.html'
    form_class = forms.ReportSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_initial(self):
        return {
            "fiscal_year": fiscal_year(sap_style=True),
        }

    def form_valid(self, form):
        report = int(form.cleaned_data["report"])
        fy = form.cleaned_data["fiscal_year"]
        user = form.cleaned_data["user"]

        if report == 1:
            return HttpResponseRedirect(reverse("travel:export_cfts_list", kwargs={
                'fy': fy,
                'user': user,
            }))
        elif report == 2:
            email = form.cleaned_data["traveller"]
            return HttpResponseRedirect(reverse("travel:travel_plan", kwargs={
                'fy': fy,
                'email': email,
            }))

        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("travel:report_search"))


def export_cfts_list(request, fy):
    file_url = reports.generate_cfts_spreadsheet(fiscal_year=fy)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="custom master list export {}.xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


def export_trip_cfts(request, pk):
    file_url = reports.generate_cfts_spreadsheet(trip=pk)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="CFTS export {}.xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404

class TravelPlanPDF(TravelAccessRequiredMixin, PDFTemplateView):
    login_url = '/accounts/login_required/'

    def get_template_names(self):
        my_object = models.Event.objects.get(id=self.kwargs['pk'])
        if my_object.is_group_trip:
            template_name = "travel/group_travel_plan.html"
        else:
            template_name = "travel/travel_plan.html"
        return template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = models.Event.objects.get(id=self.kwargs['pk'])
        context["object"] = my_object
        context["purpose_list"] = models.Purpose.objects.all()

        key_list = [
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
        ]
        total_dict = {}

        # first, let's create an object list; if this is
        if my_object.is_group_trip:
            object_list = my_object.children_events.all()
        else:
            object_list = models.Event.objects.filter(pk=my_object.id)

        for key in key_list:
            # registration is not in the travel plan form. therefore it should be added under the 'other' category
            if key == "other":
                total_dict[key] = nz(object_list.values(key).order_by(key).aggregate(dsum=Sum(key))['dsum'], 0) + \
                                  nz(object_list.values('registration').order_by('registration').aggregate(dsum=Sum("registration"))[
                                         'dsum'], 0)
                # if the sum is zero, blank it out so that it will be treated on par with other null fields in template
                if total_dict[key] == 0:
                    total_dict[key] = None
            else:
                total_dict[key] = object_list.values(key).order_by(key).aggregate(dsum=Sum(key))['dsum']
        context['total_dict'] = total_dict
        context['key_list'] = key_list
        return context


# SETTINGS #
############

@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def delete_status(request, pk):
    my_obj = models.Status.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("travel:manage_statuses"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def manage_statuses(request):
    qs = models.Status.objects.all()
    if request.method == 'POST':
        formset = forms.StatusFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("travel:manage_statuses"))
    else:
        formset = forms.StatusFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'used_for',
        'name',
        'nom',
        'order',
        'color',
    ]
    context['title'] = "Manage Statuses"
    context['formset'] = formset
    return render(request, 'travel/manage_settings_small.html', context)
