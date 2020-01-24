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
from . import utils

from shared_models import models as shared_models


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'travel/close_me.html'


def in_travel_admin_group(user):
    if user.id:
        return user.groups.filter(name='travel_admin').count() != 0


def is_approver(user, trip_request):
    if user == trip_request.current_reviewer.user:
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
        my_trip_request = models.TripRequest.objects.get(pk=self.kwargs.get("pk"))
        my_user = self.request.user
        if in_travel_admin_group(my_user) or is_approver(my_user, my_trip_request):
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
        context["number_waiting"] = self.request.user.reviewers.filter(status_id=1).count()  # number of requests where review is pending
        context["admin_number_waiting"] = models.Reviewer.objects.filter(
            status_id=1,
            role_id__in=[5,6],
        ).filter(
            ~Q(trip_request__status_id=16)
        ).count()  # number of requests where admin review is pending
        context["is_reviewer"] = True if self.request.user.reviewers.all().count() > 0 else False
        context["is_admin"] = in_travel_admin_group(self.request.user)
        return context


request_field_list = [
    'fiscal_year',
    'status_string|{}'.format(_("Request status")),
    'user',
    'section',
    'first_name',
    'last_name',
    'address',
    'phone',
    'email',
    'is_public_servant',
    'company_name',
    'region',
    'departure_location',
    'destination',
    'start_date',
    'end_date',
    # 'is_adm_approval_required',
    'purpose',
    'reason',
    # 'is_conference',
    'conference',
    # 'has_event_template',
    # 'event_lead',

    # purpose
    'role',
    'role_of_participant',
    'objective_of_event',
    'benefit_to_dfo',
    'multiple_conferences_rationale',
    'multiple_attendee_rationale',
    'late_justification',
    'bta_attendees',
    'notes',

    # costs
    # 'air',
    # 'rail',
    # 'rental_motor_vehicle',
    # 'personal_motor_vehicle',
    # 'taxi',
    # 'other_transport',
    # 'accommodations',
    # 'meals',
    # 'incidentals',
    # 'registration',
    # 'other',
    'cost_table|{}'.format(_("DFO costs")),
    # 'total_cost',
    'non_dfo_costs',
    'non_dfo_org',
    # 'cost_breakdown|{}'.format(_("cost summary")),
    # 'purpose_long|{}'.format(_("purpose")),
]

request_group_field_list = [
    'fiscal_year',
    'status_string|{}'.format(_("Request status")),
    'user',
    'section',
    'destination',
    'start_date',
    'end_date',
    # 'is_adm_approval_required',
    'purpose',
    'reason',
    # 'is_conference',
    'conference',
    # 'has_event_template',
    # 'event_lead',

    'objective_of_event',
    'benefit_to_dfo',
    'multiple_attendee_rationale',
    'funding_source',
    'bta_attendees',
    'late_justification',
    'notes',
    'total_request_cost|{}'.format(_("Total cost (DFO)")),
    'non_dfo_costs',
    'non_dfo_org',
]

request_child_field_list = [
    'first_name',
    'last_name',
    'is_public_servant',
    'is_research_scientist',
    'region',
    'start_date',
    'end_date',
    'departure_location',
    'role',
    'role_of_participant',
    'total_cost',
]

reviewer_field_list = [
    'order',
    'user',
    'role',
    'status',
    'status_date',
    'comments_html|Comments',
]

conf_field_list = [
    'tname|{}'.format(_("Name")),
    'location',
    'lead',
    'has_event_template',
    'number',
    'start_date',
    'end_date',
    'meeting_url',
    'abstract_deadline',
    'registration_deadline',
    'is_adm_approval_required',
    'notes',
    'total_cost|{}'.format("Total cost (from all connected requests, excluding BTA travel)"),
]


def get_help_text_dict():
    my_dict = {}
    for obj in models.HelpText.objects.all():
        my_dict[obj.field_name] = str(obj)

    return my_dict


# TRIP REQUEST #
################
class TripRequestListView(TravelAccessRequiredMixin, FilterView):
    queryset = models.TripRequest.objects.filter(parent_request__isnull=True)
    filterset_class = filters.TripRequestFilter
    template_name = 'travel/trip_request_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.TripRequest.objects.first()
        context["field_list"] = [
            'fiscal_year',
            'is_group_request',
            'status',
            'section',
            'first_name',
            'last_name',
            'conference.tname',
            'destination',
            'start_date',
            'end_date',
            'total_request_cost|{}'.format(_("Total request cost (DFO)")),

        ]
        return context


class TripRequestReviewListView(TravelAccessRequiredMixin, ListView):
    model = models.TripRequest
    template_name = 'travel/trip_request_review_list.html'

    def get_queryset(self):
        if self.kwargs.get("which_ones") == "awaiting":
            qs = models.TripRequest.objects.filter(pk__in=[reviewer.trip_request.id for reviewer in self.request.user.reviewers.filter(status_id=1)])
        else:
            qs = models.TripRequest.objects.filter(pk__in=[reviewer.trip_request.id for reviewer in self.request.user.reviewers.all()])
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.TripRequest.objects.first()
        context["awaiting"] = True if self.kwargs.get("which_ones") else False
        context["field_list"] = [
            'status_string|{}'.format(_("Request status")),
            'is_group_request',
            'first_name',
            'last_name',
            'conference',
            'destination',
            'start_date',
            'end_date',
            'total_request_cost|{}'.format(_("Total cost (DFO)")),
        ]
        return context


class TripRequestAdminApprovalListView(TravelAdminRequiredMixin, ListView):
    model = models.TripRequest
    template_name = 'travel/trip_request_review_list.html'

    def get_queryset(self):
        # return a list only of those awaiting ADM or RDG approval
        qs = models.TripRequest.objects.filter(
            parent_request__isnull=True,
        ).filter(status_id__in=[14, 15]).order_by("-submitted")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.TripRequest.objects.first()
        context["admin"] = True
        context["field_list"] = [
            'is_group_request',
            'first_name',
            'last_name',
            'conference',
            'destination',
            'start_date',
            'end_date',
            'total_request_cost|{}'.format(_("Total cost (DFO)")),
        ]
        return context


class TripRequestDetailView(TravelAccessRequiredMixin, DetailView):
    model = models.TripRequest
    template_name = 'travel/trip_request_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = self.get_object()
        context["field_list"] = request_field_list if not my_object.is_group_request else request_group_field_list
        my_request_child_field_list = deepcopy(request_child_field_list)
        context["child_field_list"] = my_request_child_field_list
        context["reviewer_field_list"] = reviewer_field_list
        context["conf_field_list"] = conf_field_list
        context["fy"] = fiscal_year()
        context["is_admin"] = "travel_admin" in [group.name for group in self.request.user.groups.all()]
        context["is_owner"] = my_object.user == self.request.user

        if context["is_admin"]:
            is_current_reviewer = True
        else:
            is_current_reviewer = my_object.current_reviewer.user == self.request.user if my_object.current_reviewer else None

        context["is_current_reviewer"] = is_current_reviewer
        if my_object.submitted and not is_current_reviewer:
            context["report_mode"] = True

        return context


class TripRequestUpdateView(TravelAccessRequiredMixin, UpdateView):
    model = models.TripRequest

    def get_template_names(self):
        return 'travel/trip_request_form_popout.html' if self.kwargs.get("pop") else 'travel/trip_request_form.html'

    def get_form_class(self):
        return forms.ChildTripRequestForm if self.kwargs.get("pop") else forms.TripRequestForm

    def form_valid(self, form):
        my_object = form.save()
        if not my_object.parent_request:
            if form.cleaned_data.get("stay_on_page"):
                return HttpResponseRedirect(reverse_lazy("travel:request_edit", kwargs={"pk": my_object.id}))
            else:
                return HttpResponseRedirect(reverse_lazy("travel:request_detail", kwargs={"pk": my_object.id}))
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

        conf_dict = {}
        for conf in models.Conference.objects.all():
            conf_dict[conf.id] = {}
            conf_dict[conf.id]['location'] = conf.location
            conf_dict[conf.id]['start_date'] = conf.start_date.strftime("%Y-%m-%d")
            conf_dict[conf.id]['end_date'] = conf.end_date.strftime("%Y-%m-%d")

        conf_json = json.dumps(conf_dict)
        # send JSON file to template so that it can be used by js script
        context['conf_json'] = conf_json
        context['help_text_dict'] = get_help_text_dict()

        return context


class ReviewerApproveUpdateView(AdminOrApproverRequiredMixin, UpdateView):
    model = models.Reviewer
    form_class = forms.ReviewerApprovalForm
    template_name = 'travel/reviewer_approval_form.html'

    def test_func(self):
        my_trip_request = self.get_object().trip_request
        my_user = self.request.user
        print(in_travel_admin_group(my_user) or is_approver(my_user, my_trip_request))
        if in_travel_admin_group(my_user) or is_approver(my_user, my_trip_request):
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = self.get_object()
        context["field_list"] = request_field_list if not my_object.trip_request.is_group_request else request_group_field_list
        context["child_field_list"] = request_child_field_list
        context["reviewer_field_list"] = reviewer_field_list
        context["conf_field_list"] = conf_field_list
        context["triprequest"] = my_object.trip_request
        context["report_mode"] = True
        if my_object.role_id in [5, 6, ]:
            context["admin"] = True

        return context

    def form_valid(self, form):
        my_reviewer = form.save(commit=False)

        approved = form.cleaned_data.get("approved")
        stay_on_page = form.cleaned_data.get("stay_on_page")
        changes_requested = form.cleaned_data.get("changes_requested")
        print("stay on page", stay_on_page)
        # first scenario: changes were requested for the request
        # in this case, the reviewer status does not change but the request status will
        if not stay_on_page:
            if changes_requested:
                my_reviewer.trip_request.status_id = 16
                my_reviewer.trip_request.submitted = None
                my_reviewer.trip_request.save()
                # send an email to the request owner
                my_email = emails.ChangesRequestedEmail(my_reviewer.trip_request)
                # send the email object
                if settings.PRODUCTION_SERVER:
                    send_mail(message='', subject=my_email.subject, html_message=my_email.message, from_email=my_email.from_email,
                              recipient_list=my_email.to_list, fail_silently=False, )
                else:
                    print(my_email)
                messages.success(self.request, _("Success! An email has been sent to the trip request owner."))

            # if it was approved, then we change the reviewer status to 'approved'
            elif approved:
                my_reviewer.status_id = 2
                my_reviewer.status_date = timezone.now()
            # if it was approved, then we change the reviewer status to 'approved'
            else:
                my_reviewer.status_id = 3
                my_reviewer.status_date = timezone.now()

        # now we save the reviewer for real
        my_reviewer.save()

        # update any statuses if necessary
        utils.approval_seeker(my_reviewer.trip_request)

        if stay_on_page:
            return HttpResponseRedirect(reverse("travel:review_approve", kwargs={"pk": my_reviewer.id}))
        else:
            return HttpResponseRedirect(reverse("travel:index"))



class SkipReviewerUpdateView(TravelAdminRequiredMixin, UpdateView):
    model = models.Reviewer
    form_class = forms.ReviewerSkipForm
    template_name = 'travel/reviewer_skip_form.html'

    def test_func(self):
        my_trip_request = self.get_object().trip_request
        my_user = self.request.user
        print(in_travel_admin_group(my_user) or is_approver(my_user, my_trip_request))
        if in_travel_admin_group(my_user) or is_approver(my_user, my_trip_request):
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = self.get_object()
        return context

    def form_valid(self, form):
        # if the form is submitted, that means the admin user has decided to go ahead with the manual skip
        my_reviewer = form.save(commit=False)
        my_reviewer.status_id = 21
        my_reviewer.status_date = timezone.now()
        my_reviewer.comments = "This step was manually overridden by {} with the following rationale: \n\n {}".format(self.request.user, my_reviewer.comments)

        # now we save the reviewer for real
        my_reviewer.save()

        # update any statuses if necessary
        utils.approval_seeker(my_reviewer.trip_request)

        return HttpResponseRedirect(reverse("shared_models:close_me"))


class TripRequestSubmitUpdateView(TravelAccessRequiredMixin, FormView):
    model = models.TripRequest
    form_class = forms.TripRequestApprovalForm
    template_name = 'travel/trip_request_submission_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = models.TripRequest.objects.get(pk=self.kwargs.get("pk"))
        context["object"] = my_object
        context["triprequest"] = my_object
        context["field_list"] = request_field_list if not my_object.is_group_request else request_group_field_list
        context["child_field_list"] = request_child_field_list
        context["reviewer_field_list"] = reviewer_field_list
        context["conf_field_list"] = conf_field_list
        context["report_mode"] = True

        return context

    def form_valid(self, form):
        my_trip_request = models.TripRequest.objects.get(pk=self.kwargs.get("pk"))
        # figure out the current state of the request
        is_submitted = True if my_trip_request.submitted else False

        # if submitted, then unsumbit but only if admin or owner
        if is_submitted:
            #  UNSUBMIT REQUEST
            if in_travel_admin_group(self.request.user) or my_trip_request.user == self.request.user:
                my_trip_request.submitted = None
                # reset all the reviewer statuses
                utils.end_review_process(my_trip_request)
            else:
                messages.error(self.request, "sorry, only admins or owners can unsubmit requests")
        else:
            #  SUBMIT REQUEST
            my_trip_request.submitted = timezone.now()
            # if the request is being resubmitted, this is a special case...
            if my_trip_request.status_id == 16:
                my_trip_request.status_id = 8
                my_trip_request.save()
            else:
                # set all the reviewer statuses to 'queued'
                utils.start_review_process(my_trip_request)
                # go and get approvals!!

        # No matter what business what done, we will call this function to sort through reviewer and request statuses
        utils.approval_seeker(my_trip_request)
        my_trip_request.save()
        return HttpResponseRedirect(reverse("travel:request_detail", kwargs={"pk": my_trip_request.id}))


class TripRequestCreateView(TravelAccessRequiredMixin, CreateView):
    model = models.TripRequest

    def get_template_names(self):
        my_object = models.TripRequest.objects.get(pk=self.kwargs.get("pk")) if self.kwargs.get("pk") else None
        return 'travel/trip_request_form_popout.html' if my_object else 'travel/trip_request_form.html'

    def get_form_class(self):
        my_object = models.TripRequest.objects.get(pk=self.kwargs.get("pk")) if self.kwargs.get("pk") else None
        return forms.ChildTripRequestForm if my_object else forms.TripRequestForm

    def get_initial(self):
        my_object = models.TripRequest.objects.get(pk=self.kwargs.get("pk")) if self.kwargs.get("pk") else None
        return {"user": self.request.user} if not my_object else {"parent_request": my_object}

    def form_valid(self, form):
        my_object = form.save()

        # if it is a group request, add the main user as a traveller
        if my_object.is_group_request:
            models.TripRequest.objects.create(
                user=self.request.user,
                first_name=self.request.user.first_name,
                last_name=self.request.user.last_name,
                email=self.request.user.email,
                parent_request=my_object,
            )

        # add reviewers
        utils.get_reviewers(my_object)

        if not my_object.parent_request:
            if form.cleaned_data.get("stay_on_page"):
                return HttpResponseRedirect(reverse_lazy("travel:request_edit", kwargs={"pk": my_object.id}))
            else:
                return HttpResponseRedirect(reverse_lazy("travel:request_detail", kwargs={"pk": my_object.id}))
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

        conf_dict = {}
        for conf in models.Conference.objects.all():
            conf_dict[conf.id] = {}
            conf_dict[conf.id]['location'] = conf.location
            conf_dict[conf.id]['start_date'] = conf.start_date.strftime("%Y-%m-%d")
            conf_dict[conf.id]['end_date'] = conf.end_date.strftime("%Y-%m-%d")

        conf_json = json.dumps(conf_dict)
        # send JSON file to template so that it can be used by js script
        context['conf_json'] = conf_json
        context['help_text_dict'] = get_help_text_dict()

        return context


class TripRequestDeleteView(TravelAccessRequiredMixin, DeleteView):
    model = models.TripRequest
    success_message = 'The trip request was deleted successfully!'

    def get_template_names(self):
        if self.kwargs.get('pop'):
            template_name = 'travel/trip_request_confirm_delete_popout.html'
        else:
            template_name = 'travel/trip_request_confirm_delete.html'
        return template_name

    def get_success_url(self):
        if self.kwargs.get('pop'):
            success_url = reverse('shared_models:close_me')
        else:
            success_url = reverse_lazy('travel:request_list')
        return success_url

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class TripRequestCloneUpdateView(TripRequestUpdateView):
    def test_func(self):
        if self.request.user.id:
            return True

    def get_initial(self):
        my_object = models.TripRequest.objects.get(pk=self.kwargs["pk"])
        init = super().get_initial()
        init["year"] = fiscal_year(sap_style=True, next=True)
        # init["created_by"] = self.request.user
        return init

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cloned"] = True
        return context

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        old_obj = models.TripRequest.objects.get(pk=new_obj.pk)
        new_obj.pk = None
        new_obj.submitted = None
        new_obj.save()

        # add the reviewers based on the new request info
        utils.get_reviewers(new_obj)
        utils.approval_seeker(new_obj)

        # need to clone any children of the old object...
        for child_request in old_obj.children_requests.all():
            child_request.pk = None
            child_request.parent_request = new_obj
            child_request.save()

        return HttpResponseRedirect(reverse_lazy("travel:request_detail", kwargs={"pk": new_obj.id}))


class ChildTripRequestCloneUpdateView(TripRequestCreateView):
    def test_func(self):
        if self.request.user.id:
            return True

    def get_initial(self):
        my_object = models.TripRequest.objects.get(pk=self.kwargs["pk"])
        init = super().get_initial()
        init["parent_request"] = my_object.parent_request
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


@login_required(login_url='/accounts/login_required/')
# @user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def reset_reviewers(request, pk):
    my_obj = models.TripRequest.objects.get(pk=pk)
    # first remove any existing reviewers
    my_obj.reviewers.all().delete()
    # next, re-add the defaults...
    utils.get_reviewers(my_obj)
    return HttpResponseRedirect(reverse("travel:request_detail", kwargs={"pk": my_obj.id}))


# REVIEWER #
############
@login_required(login_url='/accounts/login_required/')
# @user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def delete_reviewer(request, pk):
    my_obj = models.Reviewer.objects.get(pk=pk)
    if my_obj.trip_request.submitted:
        messages.error(request, "Cannot modify reviewers while project is submitted")
        return HttpResponseRedirect(reverse("travel:request_detail", kwargs={"pk": my_obj.trip_request.id}))
    else:
        my_obj.delete()
        my_obj.trip_request.save()
        return HttpResponseRedirect(reverse("travel:manage_reviewers", kwargs={"trip_request": my_obj.trip_request.id}))


@login_required(login_url='/accounts/login_required/')
# @user_passes_test(is_superuser, login_url='/accounts/denied/')
def manage_reviewers(request, trip_request):
    my_trip_request = models.TripRequest.objects.get(pk=trip_request)
    if my_trip_request.submitted:
        messages.error(request, "Cannot modify reviewers while project is submitted")
        return HttpResponseRedirect(reverse("travel:request_detail", kwargs={"pk": my_trip_request.id}))
    else:
        qs = models.Reviewer.objects.filter(trip_request=my_trip_request)
        if request.method == 'POST':
            formset = forms.ReviewerFormSet(request.POST)

            if formset.is_valid():
                formset.save()

                my_trip_request.save()
                # do something with the formset.cleaned_data
                messages.success(request, _("The reviewer list has been successfully updated"))
                return HttpResponseRedirect(reverse("travel:manage_reviewers", kwargs={"trip_request": my_trip_request.id}))
        else:
            formset = forms.ReviewerFormSet(
                queryset=qs,
                initial=[{"trip_request": my_trip_request}],
            )

        context = {}
        context['triprequest'] = my_trip_request
        context['formset'] = formset
        context["my_object"] = models.Reviewer.objects.first()
        context["field_list"] = [
            'trip_request',
            'order',
            'user',
            'role',
        ]
        return render(request, 'travel/reviewer_formset.html', context)


# CONFERENCE #
##############

class ConferenceListView(TravelAccessRequiredMixin, FilterView):
    model = models.Conference
    filterset_class = filters.ConferenceFilter
    template_name = 'travel/conference_list.html'

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"fiscal_year": fiscal_year(next=False, sap_style=True)}
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Conference.objects.first()
        context["field_list"] = [
            'fiscal_year',
            'tname|{}'.format("Name"),
            'location|{}'.format(_("location")),
            'dates|{}'.format(_("dates")),
            'number_of_days|{}'.format(_("length (days)")),
            'is_adm_approval_required|{}'.format(_("ADM approval required?")),
        ]
        context["is_admin"] = in_travel_admin_group(self.request.user)
        return context


class ConferenceDetailView(TravelAccessRequiredMixin, DetailView):
    model = models.Conference

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["conf_field_list"] = conf_field_list
        return context


class ConferenceUpdateView(TravelAdminRequiredMixin, UpdateView):
    model = models.Conference
    form_class = forms.ConferenceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()

        return context


class ConferenceCreateView(TravelAccessRequiredMixin, CreateView):
    model = models.Conference
    form_class = forms.ConferenceForm

    def get_template_names(self):
        if self.kwargs.get("pop"):
            return 'travel/conference_form_popout.html'
        else:
            return 'travel/conference_form.html'

    def get_success_url(self):
        if self.kwargs.get("pop"):
            return reverse("shared_models:close_me")
        else:
            return super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()

        return context

    def form_valid(self, form):
        my_object = form.save()
        if self.kwargs.get("pop"):
            # create a new email object
            email = emails.NewTripEmail(my_object)
            # send the email object
            if settings.PRODUCTION_SERVER:
                send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
                          recipient_list=email.to_list, fail_silently=False, )
            else:
                print(email)
            messages.success(self.request,
                             _("The trip has been added to the database!"))
        return super().form_valid(form)


class ConferenceDeleteView(TravelAdminRequiredMixin, DeleteView):
    model = models.Conference
    success_url = reverse_lazy('travel:conf_list')
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


def export_request_cfts(request, pk):
    file_url = reports.generate_cfts_spreadsheet(trip_request=pk)

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
        my_object = models.TripRequest.objects.get(id=self.kwargs['pk'])
        if my_object.is_group_request:
            template_name = "travel/group_travel_plan.html"
        else:
            template_name = "travel/travel_plan.html"
        return template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = models.TripRequest.objects.get(id=self.kwargs['pk'])
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
        if my_object.is_group_request:
            object_list = my_object.children_requests.filter(
                Q(region=my_object.section.division.branch.region) | Q(region__isnull=True) | Q(is_public_servant=False))
        else:
            object_list = models.TripRequest.objects.filter(pk=my_object.id)

        for key in key_list:
            # registration is not in the travel plan form. therefore it should be added under the 'other' category
            if key == "other":
                total_dict[key] = nz(object_list.values(key).order_by(key).aggregate(dsum=Sum(key))['dsum'], 0) + \
                                  nz(object_list.values('registration').order_by('registration').aggregate(dsum=Sum("registration"))[
                                         'dsum'], 0)
                # if the sum is zero, blank it out so that it will be treated on par with other null fields in template
                if total_dict[key] == 0:
                    total_dict[key] = None
            elif key == "meals":
                total_dict[key] = nz(object_list.values('breakfasts').order_by('breakfasts').aggregate(dsum=Sum("breakfasts"))[
                                         'dsum'], 0) + \
                                  nz(object_list.values('lunches').order_by('lunches').aggregate(dsum=Sum("lunches"))[
                                         'dsum'], 0) + \
                                  nz(object_list.values('suppers').order_by('suppers').aggregate(dsum=Sum("suppers"))[
                                         'dsum'], 0)

                # if the sum is zero, blank it out so that it will be treated on par with other null fields in template
                if total_dict[key] == 0:
                    total_dict[key] = None
            else:
                total_dict[key] = object_list.values(key).order_by(key).aggregate(dsum=Sum(key))['dsum']
        context['object_list'] = object_list
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


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def delete_help_text(request, pk):
    my_obj = models.HelpText.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("travel:manage_help_text"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def manage_help_text(request):
    qs = models.HelpText.objects.all()
    if request.method == 'POST':
        formset = forms.HelpTextFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("travel:manage_help_text"))
    else:
        formset = forms.HelpTextFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'field_name',
        'eng_text',
        'fra_text',
    ]
    context['title'] = "Manage Help Text"
    context['formset'] = formset
    return render(request, 'travel/manage_settings_small.html', context)


# FILES #
#########

class FileCreateView(TravelAccessRequiredMixin, CreateView):
    template_name = "travel/file_form.html"
    model = models.File
    form_class = forms.FileForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse("shared_models:close_me"))

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        context["editable"] = True
        trip_request = models.TripRequest.objects.get(pk=self.kwargs['trip_request'])
        context["triprequest"] = trip_request
        return context

    def get_initial(self):
        trip_request = models.TripRequest.objects.get(pk=self.kwargs['trip_request'])
        # status_report = models.StatusReport.objects.get(pk=self.kwargs['status_report']) if self.kwargs.get('status_report') else None

        return {
            'trip_request': trip_request,
        }


class FileUpdateView(TravelAccessRequiredMixin, UpdateView):
    template_name = "travel/file_form.html"
    model = models.File
    form_class = forms.FileForm

    def get_success_url(self, **kwargs):
        return reverse_lazy("travel:file_detail", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        context["editable"] = True
        return context


class FileDetailView(FileUpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["editable"] = False
        return context


class FileDeleteView(TravelAccessRequiredMixin, DeleteView):
    template_name = "travel/file_confirm_delete.html"
    model = models.File

    def get_success_url(self, **kwargs):
        return reverse_lazy("shared_models:close_me")
