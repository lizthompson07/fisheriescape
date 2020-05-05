import json
import os
from copy import deepcopy

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models.functions import Concat
from django.utils.safestring import mark_safe

from dm_apps.utils import custom_send_mail
from django.db.models import Sum, Q, Value, TextField
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
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


def get_conf_details(request):
    conf_dict = {}
    for conf in models.Conference.objects.all():
        conf_dict[conf.id] = {}
        conf_dict[conf.id]['location'] = conf.location
        conf_dict[conf.id]['start_date'] = conf.start_date.strftime("%Y-%m-%d")
        conf_dict[conf.id]['end_date'] = conf.end_date.strftime("%Y-%m-%d")

    return JsonResponse(conf_dict)


def in_travel_admin_group(user):
    if user.id:
        return user.groups.filter(name='travel_admin').count() != 0


def in_adm_admin_group(user):
    if user.id:
        return user.groups.filter(name='travel_adm_admin').count() != 0


def is_approver(user, trip_request):
    if trip_request.current_reviewer and user == trip_request.current_reviewer.user:
        return True


def can_modify_request(user, trip_request_id, trip_request_unsubmit=False):
    """
    returns True if user has permissions to delete or modify a request

    The answer of this question will depend on whether the trip is submitted.
    owners cannot edit a submitted trip

    :param user:
    :param trip_request_id:
    :param trip_request_submit: If true, it means this function is being used to answer the question about whether a user can unsubmit a trip
    :return:
    """
    if user.id:
        my_trip_request = models.TripRequest.objects.get(pk=trip_request_id)

        # check to see if a travel_admin
        if in_travel_admin_group(user):
            return True

        # check to see if they are the active reviewer
        # determine if this is a child trip or not.
        if not my_trip_request.parent_request:
            if my_trip_request.current_reviewer and my_trip_request.current_reviewer.user == user:
                return True
        # This is a child trip request
        else:
            if my_trip_request.parent_request.current_reviewer and my_trip_request.parent_request.current_reviewer.user == user:
                return True
        # if the project is unsubmitted, the project lead is also able to edit the project... obviously
        # check to see if they are either the owner OR a traveller
        # SPECIAL CASE: sometimes we complete requests on behalf of somebody else.
        if not my_trip_request.submitted and \
                (not my_trip_request.user or  # anybody can edit
                 my_trip_request.user == user or  # the user is the traveller and / or requester
                 user in my_trip_request.travellers or  # the user is a traveller on the trip
                 (my_trip_request.parent_request and my_trip_request.parent_request.user == user)):  # the user is the requester
            return True

        if trip_request_unsubmit and user == my_trip_request.user:
            return True


class TravelAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_travel_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class TravelADMAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_adm_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class CanModifyMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return can_modify_request(self.request.user, self.kwargs.get("pk"))

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class AdminOrApproverRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

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
    login_url = '/accounts/login/'


class IndexTemplateView(TravelAccessRequiredMixin, TemplateView):
    template_name = 'travel/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # show the number of reviews awaiting for the logged in user
        context["reviews_waiting"] = self.request.user.reviewers.filter(status_id=1).filter(
            ~Q(trip_request__status_id=16)).count()  # number of requests where review is pending

        # this will be the dict to populate the tabs on the index page
        tab_dict = dict()
        for region in shared_models.Region.objects.filter(~Q(id=6)):
            tab_dict[region] = dict()
            # this will be the counter for any of the things that need dealing with

            # RDG
            rdg_number_waiting = models.Reviewer.objects.filter(
                status_id=1,
                role_id=6,
                trip_request__section__division__branch__region=region,
            ).filter(~Q(trip_request__status_id=16)).count()  # number of requests where admin review is pending
            rdg_approval_list_url = reverse('travel:admin_approval_list', kwargs={"type": 'rdg', "region": region.id})

            # ADM
            adm_number_waiting = models.Reviewer.objects.filter(
                status_id=1,
                role_id=5,
                trip_request__section__division__branch__region=region,
            ).filter(~Q(trip_request__status_id=16)).count()  # number of requests where admin review is pending
            adm_approval_list_url = reverse('travel:admin_approval_list', kwargs={"type": 'adm', "region": region.id})

            # unverified trips
            unverified_trips = models.Conference.objects.filter(status_id=30, is_adm_approval_required=False, lead=region).count()
            trip_verification_list_url = reverse('travel:admin_trip_verification_list', kwargs={"adm": 0, "region": region.id})

            tab_dict[region]["rdg_number_waiting"] = rdg_number_waiting
            tab_dict[region]["rdg_approval_list_url"] = rdg_approval_list_url
            tab_dict[region]["adm_number_waiting"] = adm_number_waiting
            tab_dict[region]["adm_approval_list_url"] = adm_approval_list_url
            tab_dict[region]["unverified_trips"] = unverified_trips
            tab_dict[region]["trip_verification_list_url"] = trip_verification_list_url
            tab_dict[region]["things_to_deal_with"] = rdg_number_waiting + adm_number_waiting + unverified_trips

        # Now for NCR
        tab_dict["NCR"] = dict()

        # unverified trips
        unverified_trips = models.Conference.objects.filter(status_id=30, is_adm_approval_required=True).count()
        trip_verification_list_url = reverse('travel:admin_trip_verification_list', kwargs={"adm": 1, "region": 0})
        tab_dict["NCR"]["unverified_trips"] = unverified_trips
        tab_dict["NCR"]["trip_verification_list_url"] = trip_verification_list_url
        tab_dict["NCR"]["things_to_deal_with"] = unverified_trips  # placeholder :)

        context["is_reviewer"] = True if self.request.user.reviewers.all().count() > 0 else False
        context["is_admin"] = in_travel_admin_group(self.request.user)
        context["is_adm_admin"] = in_adm_admin_group(self.request.user)
        context["tab_dict"] = tab_dict

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
    'purpose',
    'reason',
    'trip',

    'role',
    'role_of_participant',
    'objective_of_event',
    'benefit_to_dfo',
    'multiple_conferences_rationale',
    'multiple_attendee_rationale',
    'late_justification',
    'bta_attendees',
    'notes',
    # 'cost_table|{}'.format(_("DFO costs")),
    'total_request_cost|{}'.format(_("Total costs")),
    'total_dfo_funding|{}'.format(_("Total amount of DFO funding")),
    'total_non_dfo_funding|{}'.format(_("Total amount of non-DFO funding")),
    'total_non_dfo_funding_sources|{}'.format(_("Non-DFO funding sources")),
    'original_submission_date',
    'processing_time|{}'.format(_("Processing time")),
]

request_group_field_list = [
    'fiscal_year',
    'status_string|{}'.format(_("Request status")),
    'user',
    'section',
    'destination',
    'purpose',
    'reason',
    'trip',

    'objective_of_event',
    'benefit_to_dfo',
    'multiple_attendee_rationale',
    'funding_source',
    'bta_attendees',
    'late_justification',
    'notes',
    'total_dfo_funding|{}'.format(_("Total amount of DFO funding")),
    'total_non_dfo_funding|{}'.format(_("Total amount of non-DFO funding")),
    'total_non_dfo_funding_sources|{}'.format(_("Non-DFO funding sources")),
    'total_request_cost|{}'.format(_("Total cost")),
    'original_submission_date',
    'processing_time|{}'.format(_("Processing time")),
]

request_child_field_list = [
    'requester_name|{}'.format(_("Name")),
    # 'is_public_servant',
    'is_research_scientist|{}'.format(_("RES?")),
    # 'region',
    'dates|{}'.format(_("Travel dates")),
    'departure_location',
    'role',
    'role_of_participant',
    'total_cost|{}'.format(_("Total cost")),
    'non_dfo_costs|{}'.format(_("non-DFO funding")),

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
    'status',
    'total_cost|{}'.format("Total DFO cost (excluding BTA)"),
    'non_res_total_cost|{}'.format("Total DFO cost from non-RES travellers (excluding BTA)"),
]

cost_field_list = [
    "cost",
    "rate_cad",
    "number_of_days",
    "amount_cad",
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
        context["subtitle"] = _("Trip Requests")
        context["h1"] = _("Trip Requests")
        context["crumbs"] = [
            {"title": _("Home"), "url": reverse("travel:index")},
            {"title": context["h1"]}
        ]

        context["paginate_by"] = 25
        context["container_class"] = "container-fluid"
        context["new_url_name"] = "travel:request_new"
        context["row_url_name"] = "travel:request_detail"
        context["random_object"] = models.TripRequest.objects.first()
        context["field_list"] = [
            {"name": 'fiscal_year', "width": "75px"},
            {"name": 'is_group_request|Type', },
            {"name": 'status', "width": "150px"},
            {"name": 'section|{}'.format(_("DFO section")), },
            {"name": 'requester_name|{}'.format(_("Requester name")), },
            {"name": 'trip.tname', "width": "400px"},
            {"name": 'destination|{}'.format(_("Destination")), },
            {"name": 'start_date|{}'.format(_("Departure date")), },
            {"name": 'processing_time|{}'.format(_("Processing time")), },
        ]
        return context


class TripRequestReviewListView(TravelAccessRequiredMixin, ListView):
    model = models.TripRequest
    template_name = 'travel/trip_request_review_list.html'

    def get_queryset(self):
        if self.kwargs.get("which_ones") == "awaiting":
            qs = models.TripRequest.objects.filter(
                pk__in=[reviewer.trip_request.id for reviewer in self.request.user.reviewers.filter(status_id=1)])
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
            'trip',
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
        qs = models.TripRequest.objects.filter(parent_request__isnull=True).order_by("-submitted")
        if self.kwargs.get("type") == "adm":
            qs = qs.filter(status_id=14)
        elif self.kwargs.get("type") == "rdg":
            qs = qs.filter(status_id=15)
        if self.kwargs.get("region"):
            qs = qs.filter(section__division__branch__region_id=self.kwargs.get("region"))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.TripRequest.objects.first()
        context["admin"] = True
        context["type_bilingual"] = _(self.kwargs.get("type")).upper()

        context["field_list"] = [
            'is_group_request',
            'first_name',
            'last_name',
            'trip',
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
        context["cost_field_list"] = cost_field_list
        context['help_text_dict'] = get_help_text_dict()
        context["fy"] = fiscal_year()
        context["is_admin"] = "travel_admin" in [group.name for group in self.request.user.groups.all()]
        context["is_owner"] = my_object.user == self.request.user

        # Admins should be given the same permissions as a current reviewer; the two are synonymous
        if context["is_admin"]:
            is_current_reviewer = True
        else:
            is_current_reviewer = my_object.current_reviewer.user == self.request.user if my_object.current_reviewer else None

        context["is_current_reviewer"] = is_current_reviewer
        if my_object.submitted and not is_current_reviewer:
            context["report_mode"] = True

        # This might be a better thing to use for button disabling
        context["can_modify"] = can_modify_request(self.request.user, my_object.id)
        return context


class TripRequestUpdateView(CanModifyMixin, UpdateView):
    model = models.TripRequest

    def get_initial(self):
        return {"reset_reviewers": False}

    def get_template_names(self):
        return 'travel/trip_request_form_popout.html' if self.kwargs.get("pop") else 'travel/trip_request_form.html'

    def get_form_class(self):
        return forms.ChildTripRequestForm if self.kwargs.get("pop") else forms.TripRequestForm

    def form_valid(self, form):
        my_object = form.save()

        if my_object.parent_request:
            my_trip = my_object.parent_request.trip
        else:
            my_trip = my_object.trip
        utils.manage_trip_warning(my_trip)

        # decide whether the reviewers should be reset
        if form.cleaned_data.get("reset_reviewers"):
            reset_reviewers(self.request, my_object.pk)

        if not my_object.parent_request:
            if form.cleaned_data.get("stay_on_page"):
                return HttpResponseRedirect(reverse_lazy("travel:request_edit", kwargs={"pk": my_object.id}))
            else:
                return HttpResponseRedirect(reverse_lazy("travel:request_detail", kwargs={"pk": my_object.id}))
        else:
            return HttpResponseRedirect(reverse("shared_models:close_me"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cost_field_list"] = cost_field_list

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
        # print(in_travel_admin_group(my_user) or is_approver(my_user, my_trip_request))
        if in_travel_admin_group(my_user) or is_approver(my_user, my_trip_request):
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = self.get_object()
        context["field_list"] = request_field_list if not my_object.trip_request.is_group_request else request_group_field_list
        context["child_field_list"] = request_child_field_list
        context["reviewer_field_list"] = reviewer_field_list
        context["conf_field_list"] = conf_field_list
        context["cost_field_list"] = cost_field_list
        context['help_text_dict'] = get_help_text_dict()

        context["triprequest"] = my_object.trip_request
        context["report_mode"] = True
        if my_object.role_id in [5, 6, ]:
            context["admin"] = True
            context["type_bilingual"] = _(self.kwargs.get("type")).upper()
        return context

    def form_valid(self, form):
        # don't save the reviewer yet because there are still changes to make
        my_reviewer = form.save(commit=True)

        approved = form.cleaned_data.get("approved")
        stay_on_page = form.cleaned_data.get("stay_on_page")
        changes_requested = form.cleaned_data.get("changes_requested")
        # first scenario: changes were requested for the request
        # in this case, the reviewer status does not change but the request status will
        if not stay_on_page:
            if changes_requested:
                my_reviewer.trip_request.status_id = 16
                my_reviewer.trip_request.submitted = None
                my_reviewer.trip_request.save()
                # send an email to the request owner
                email = emails.ChangesRequestedEmail(my_reviewer.trip_request)
                # send the email object
                custom_send_mail(
                    subject=email.subject,
                    html_message=email.message,
                    from_email=email.from_email,
                    recipient_list=email.to_list
                )
                messages.success(self.request, _("Success! An email has been sent to the trip request owner."))

            # if it was approved, then we change the reviewer status to 'approved'
            elif approved:
                my_reviewer.status_id = 2
                my_reviewer.status_date = timezone.now()
                my_reviewer.save()
            # if it was approved, then we change the reviewer status to 'approved'
            else:
                my_reviewer.status_id = 3
                my_reviewer.status_date = timezone.now()
                my_reviewer.save()

        # update any statuses if necessary
        utils.approval_seeker(my_reviewer.trip_request)

        if stay_on_page:
            my_kwargs = {"pk": my_reviewer.id}
            # if this is an adm or rdg review, we have to pass the type into the url.
            if my_reviewer.role_id in [5, 6, ]:
                my_kwargs.update({"type": self.kwargs.get("type")})
            return HttpResponseRedirect(reverse("travel:review_approve", kwargs=my_kwargs))
        else:
            # This means that they have approved or did not approve...
            return HttpResponseRedirect(reverse("travel:request_review_list", kwargs={"which_ones": "awaiting"}))


class SkipReviewerUpdateView(TravelAdminRequiredMixin, UpdateView):
    model = models.Reviewer
    form_class = forms.ReviewerSkipForm
    template_name = 'travel/reviewer_skip_form.html'

    def test_func(self):
        my_trip_request = self.get_object().trip_request
        my_user = self.request.user
        # print(in_travel_admin_group(my_user) or is_approver(my_user, my_trip_request))
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
        my_reviewer.comments = "This step was manually overridden by {} with the following rationale: \n\n {}".format(self.request.user,
                                                                                                                      my_reviewer.comments)

        # now we save the reviewer for real
        my_reviewer.save()

        # update any statuses if necessary
        utils.approval_seeker(my_reviewer.trip_request)

        return HttpResponseRedirect(reverse("shared_models:close_me"))


class TripRequestSubmitUpdateView(CanModifyMixin, FormView):
    model = models.TripRequest
    form_class = forms.TripRequestApprovalForm
    template_name = 'travel/trip_request_submission_form.html'

    def test_func(self):
        # This view is a little different. A trip owner should always be allowed to unsubmit
        return can_modify_request(self.request.user, self.kwargs.get("pk"), True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        my_object = models.TripRequest.objects.get(pk=self.kwargs.get("pk"))

        if my_object.submitted:
            active_crumb = _("Un-submit request")
            h1 = _("Do you wish to un-submit the following request?")
            h2 = '<span class="red-font">WARNING: Un-submitting this request will reset the' \
                 ' status of any exisitng recommendations and/or approvals.</span>'
        else:
            active_crumb = _("Re-submit request") if my_object.status_id == "16" else _("Submit request")
            h1 = _("Do you wish to re-submit the following request?") if my_object.status_id == "16" else _(
                "Do you wish to submit the following request?")
            h2 = None

        context["h1"] = h1
        context["h2"] = h2

        context["subtitle"] = active_crumb
        context["back_url"] = reverse("travel:request_detail", kwargs={"pk": my_object.id})
        context["crumbs"] = [
            {"title": _("Home"), "url": reverse("travel:index")},
            {"title": _("Trip Requests"), "url": reverse("travel:request_list")},
            {"title": str(my_object), "url": context["back_url"]},
            {"title": active_crumb}
        ]

        context["object"] = my_object
        context["triprequest"] = my_object
        context["field_list"] = request_field_list if not my_object.is_group_request else request_group_field_list
        context["child_field_list"] = request_child_field_list
        context["reviewer_field_list"] = reviewer_field_list
        context["conf_field_list"] = conf_field_list
        context["cost_field_list"] = cost_field_list
        context['help_text_dict'] = get_help_text_dict()
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
                my_trip_request.status_id = 8
                my_trip_request.save()
                # reset all the reviewer statuses
                utils.end_review_process(my_trip_request)
            else:
                messages.error(self.request, "sorry, only admins or owners can unsubmit requests")
        else:
            if my_trip_request.trip.status_id != 30 and my_trip_request.trip.status_id != 41:
                messages.error(self.request, "sorry, the trip you are requesting to attend is not accepting additional requests.")
            else:

                #  SUBMIT REQUEST
                my_trip_request.submitted = timezone.now()
                # if there is not an original submission date, add one
                if not my_trip_request.original_submission_date:
                    my_trip_request.original_submission_date = timezone.now()
                # if the request is being resubmitted, this is a special case...
                if my_trip_request.status_id == 16:
                    my_trip_request.status_id = 8
                    my_trip_request.save()
                else:
                    # set all the reviewer statuses to 'queued'
                    utils.start_review_process(my_trip_request)
                    # go and get approvals!!

        # No matter what business was done, we will call this function to sort through reviewer and request statuses
        utils.approval_seeker(my_trip_request)
        my_trip_request.save()

        # clean up any unused cost categories
        utils.clear_empty_trip_request_costs(my_trip_request)
        for child in my_trip_request.children_requests.all():
            utils.clear_empty_trip_request_costs(child)

        return HttpResponseRedirect(reverse("travel:request_detail", kwargs={"pk": my_trip_request.id}))


class TripRequestCancelUpdateView(TravelAdminRequiredMixin, UpdateView):
    model = models.TripRequest
    form_class = forms.TripRequestAdminNotesForm
    template_name = 'travel/trip_request_cancel_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = models.TripRequest.objects.get(pk=self.kwargs.get("pk"))
        context["object"] = my_object
        context["triprequest"] = my_object
        context["field_list"] = request_field_list if not my_object.is_group_request else request_group_field_list
        context["child_field_list"] = request_child_field_list
        context["reviewer_field_list"] = reviewer_field_list
        context["conf_field_list"] = conf_field_list
        context["cost_field_list"] = cost_field_list
        context['help_text_dict'] = get_help_text_dict()
        context["report_mode"] = True

        return context

    def form_valid(self, form):
        my_trip_request = form.save()

        # figure out the current state of the request
        is_cancelled = True if my_trip_request.status.id == 22 else False

        if is_cancelled:
            #  UN-CANCEL THE REQUEST
            my_trip_request.status_id = 11
        else:
            #  CANCEL THE REQUEST
            my_trip_request.status_id = 22

        my_trip_request.save()
        # send an email to the trip_request owner
        email = emails.StatusUpdateEmail(my_trip_request)
        # # send the email object
        custom_send_mail(
            subject=email.subject,
            html_message=email.message,
            from_email=email.from_email,
            recipient_list=email.to_list
        )

        return HttpResponseRedirect(reverse("travel:request_detail", kwargs={"pk": my_trip_request.id}))


class TripRequestAdminNotesUpdateView(TravelAdminRequiredMixin, UpdateView):
    model = models.TripRequest
    form_class = forms.TripRequestAdminNotesForm
    template_name = 'travel/generic_popout_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["h1"] = _("Administrative Notes (Public)")
        return context

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse("shared_models:close_me"))


class TripRequestCreateView(TravelAccessRequiredMixin, CreateView):
    model = models.TripRequest

    def get_template_names(self):
        if self.kwargs.get("parent_request"):
            return 'travel/trip_request_form_popout.html'
        else:
            return 'travel/trip_request_form.html'

    def get_form_class(self):
        if self.kwargs.get("parent_request"):
            return forms.ChildTripRequestForm
        else:
            return forms.TripRequestForm

    def get_initial(self):
        if self.kwargs.get("parent_request"):
            my_object = models.TripRequest.objects.get(pk=self.kwargs.get("parent_request"))
            my_dict = {
                "parent_request": my_object,
                "stay_on_page": True,
                "start_date": my_object.trip.start_date,
                "end_date": my_object.trip.end_date,
            }
        else:
            # if this is a new parent trip
            my_dict = {"user": self.request.user}
        return my_dict

    def form_valid(self, form):
        my_object = form.save()

        # if it is a group request, add the main user as a traveller
        if my_object.is_group_request:
            my_child_object = models.TripRequest.objects.create(
                user=self.request.user,
                first_name=self.request.user.first_name,
                last_name=self.request.user.last_name,
                email=self.request.user.email,
                parent_request=my_object,
            )
            # pre-populate the costs on the 'child' record
            utils.populate_trip_request_costs(self.request, my_child_object)
        else:
            # if the request is not a group request, we pre-populate the costs on the 'parent' record
            utils.populate_trip_request_costs(self.request, my_object)

        # add reviewers
        utils.get_tr_reviewers(my_object)

        # if this is not a child record
        if not my_object.parent_request:
            if form.cleaned_data.get("stay_on_page"):
                return HttpResponseRedirect(reverse_lazy("travel:request_edit", kwargs={"pk": my_object.id}))
            else:
                return HttpResponseRedirect(reverse_lazy("travel:request_detail", kwargs={"pk": my_object.id}))
        # if this is a child record
        else:
            if form.cleaned_data.get("stay_on_page"):
                messages.success(self.request, _(
                    "{} has been added as a traveller to this request. Please add any costs associated with this traveller.".format(
                        my_object.user)))
                return HttpResponseRedirect(reverse("travel:request_edit", kwargs={"pk": my_object.id, "pop": "1"}))
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


class TripRequestDeleteView(CanModifyMixin, DeleteView):
    model = models.TripRequest

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
        my_object = self.get_object()
        my_object.delete()

        if my_object.parent_request:
            my_trip = my_object.parent_request.trip
        else:
            my_trip = my_object.trip
        utils.manage_trip_warning(my_trip)

        messages.success(self.request,
                         'The trip request for {} {} was deleted successfully!'.format(my_object.first_name, my_object.last_name))
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)


class TripRequestCloneUpdateView(TripRequestUpdateView):
    def test_func(self):
        if self.request.user.id:
            return True

    def get_initial(self):
        my_object = models.TripRequest.objects.get(pk=self.kwargs["pk"])
        init = super().get_initial()
        init["year"] = fiscal_year(sap_style=True, next=True)
        init["user"] = self.request.user
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
        utils.get_tr_reviewers(new_obj)
        utils.approval_seeker(new_obj)

        if new_obj.is_group_request:
            my_child_object = models.TripRequest.objects.create(
                user=self.request.user,
                first_name=self.request.user.first_name,
                last_name=self.request.user.last_name,
                email=self.request.user.email,
                parent_request=new_obj,
            )
            # pre-populate the costs on the 'child' record
            utils.populate_trip_request_costs(self.request, my_child_object)
        else:
            # import from old record
            # costs
            for old_rel_obj in old_obj.trip_request_costs.all():
                new_rel_obj = deepcopy(old_rel_obj)
                new_rel_obj.pk = None
                new_rel_obj.trip_request = new_obj
                new_rel_obj.save()

        # # need to clone any children of the old object...
        # for child_request in old_obj.children_requests.all():
        #     child_request.pk = None
        #     child_request.parent_request = new_obj
        #     child_request.save()

        if form.cleaned_data.get("stay_on_page"):
            return HttpResponseRedirect(reverse_lazy("travel:request_edit", kwargs={"pk": new_obj.id}))
        else:
            return HttpResponseRedirect(reverse_lazy("travel:request_detail", kwargs={"pk": new_obj.id}))


class ChildTripRequestCloneUpdateView(TripRequestUpdateView):
    def test_func(self):
        if self.request.user.id:
            return True

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        old_obj = models.TripRequest.objects.get(pk=new_obj.pk)
        new_obj.pk = None
        new_obj.submitted = None
        new_obj.save()

        # costs
        for old_rel_obj in old_obj.trip_request_costs.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.trip_request = new_obj
            new_rel_obj.save()

        return HttpResponseRedirect(reverse_lazy("travel:request_edit", kwargs={"pk": new_obj.id, "pop": "1"}))

    def get_initial(self):
        init = super().get_initial()
        init["user"] = None
        return init

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cloned"] = True
        return context


@login_required(login_url='/accounts/login/')
# @user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def reset_reviewers(request, triprequest=None, trip=None):
    """this function will reset the reviewers on either a trip request or trip
    """
    if triprequest:
        my_obj = models.TripRequest.objects.get(pk=triprequest)
        if can_modify_request(request.user, triprequest):
            # This function should only ever be run if the TR is a draft
            if my_obj.status.id == 8:
                # first remove any existing reviewers
                my_obj.reviewers.all().delete()
                # next, re-add the defaults...
                utils.get_tr_reviewers(my_obj)
            else:
                messages.error(request, _("This function can only be used when the trip request is still a draft"))
        else:
            messages.error(request, _("You do not have the permissions to reset the reviewer list"))
        return HttpResponseRedirect(reverse("travel:request_detail", kwargs={"pk": my_obj.id}))

    elif trip:
        # first, this should only ever be an ADM admin group
        if not in_adm_admin_group(request.user):
            return HttpResponseForbidden()
        else:
            my_obj = models.Conference.objects.get(pk=trip)
            # This function should only ever be run if the trip is unreviewed (30 = unverified, unreviewer; 41 = verified, reviewed)
            if my_obj.status.id in [30, 41]:
                # first remove any existing reviewers
                my_obj.reviewers.all().delete()
                # next, re-add the defaults...
                utils.get_trip_reviewers(my_obj)
            else:
                messages.error(request, _("This function can only with an unreviewed trip."))
            return HttpResponseRedirect(reverse("travel:trip_detail", kwargs={"pk": my_obj.id}))


# REVIEWER #
############
@login_required(login_url='/accounts/login/')
# @user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def delete_reviewer(request, triprequest=None, trip=None):
    if triprequest:
        my_obj = models.Reviewer.objects.get(pk=triprequest)
        if can_modify_request(request.user, my_obj.trip_request.id):
            # This function should only ever be run if the TR is in draft or changes have been requested
            # if not my_obj.trip_request.status_id in [8, 16]:
            #     messages.error(request, _("Sorry, you will have to unsubmit the trip in order to make this change"))
            #     return HttpResponseRedirect(reverse("travel:request_detail", kwargs={"pk": my_obj.trip_request.id}))
            # else:
            # now, the status of the reviewer matters.. under no circumstances should a reviewer that is not in "draft" or "queue" mode be modified / deleted
            if my_obj.status_id not in [4, 20]:
                messages.error(request, _(f"Sorry, you cannot delete a reviewer who's status is set to {my_obj.status}"))
            else:
                # it is ok to delete the reviewer
                my_obj.delete()
                my_obj.trip_request.save()
            return HttpResponseRedirect(reverse("travel:manage_reviewers", kwargs={"trip_request": my_obj.trip_request.id}))
        else:
            messages.error(request, _("You do not have the permissions to delete a reviewer"))
            return HttpResponseRedirect(reverse("travel:request_detail", kwargs={"pk": my_obj.trip_request.id}))
    else:
        if not in_adm_admin_group(request.user):
            return HttpResponseForbidden()
        else:
            my_obj = models.TripReviewer.objects.get(pk=trip)
            if my_obj.status_id not in [23, 24]:
                messages.error(request, _(f"Sorry, you cannot delete a reviewer who's status is set to {my_obj.status}"))
            else:
                # it is ok to delete the reviewer
                my_obj.delete()
                my_obj.trip.save()
            return HttpResponseRedirect(reverse("travel:manage_trip_reviewers", kwargs={"trip": my_obj.trip.id}))


@login_required(login_url='/accounts/login/')
# @user_passes_test(is_superuser, login_url='/accounts/denied/')
def manage_reviewers(request, triprequest=None, trip=None):
    if triprequest:
        my_trip_request = models.TripRequest.objects.get(pk=triprequest)
        if can_modify_request(request.user, my_trip_request.id):
            # if not my_trip_request.status_id in [8, 16]:
            #     messages.error(request, _("Sorry, you will have to unsubmit the trip in order to make this change"))
            #     return HttpResponseRedirect(reverse("travel:request_detail", kwargs={"pk": my_trip_request.id}))
            # else:
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

            context = dict()
            context['triprequest'] = my_trip_request
            context['formset'] = formset
            context["my_object"] = models.Reviewer.objects.first()
            context["field_list"] = [
                'order',
                'user',
                'role',
            ]
            return render(request, 'travel/reviewer_formset.html', context)
        else:
            messages.error(request, _("You do not have the permissions to modify the reviewer list"))
            return HttpResponseRedirect(reverse("travel:request_detail", kwargs={"pk": my_trip_request.id}))
    elif trip:
        my_trip = models.Conference.objects.get(pk=trip)
        if not in_adm_admin_group(request.user):
            return HttpResponseForbidden()
        else:
            qs = models.TripReviewer.objects.filter(trip=trip)
            if request.method == 'POST':
                formset = forms.TripReviewerFormSet(request.POST)
                if formset.is_valid():
                    formset.save()

                    my_trip.save()
                    # do something with the formset.cleaned_data
                    messages.success(request, _("The reviewer list has been successfully updated"))
                    return HttpResponseRedirect(reverse("travel:manage_reviewers", kwargs={"trip": my_trip.id}))
            else:
                formset = forms.TripReviewerFormSet(
                    queryset=qs,
                    initial=[{"trip": my_trip}],
                )

            context = dict()
            context['trip'] = my_trip
            context['formset'] = formset
            context["my_object"] = models.TripReviewer.objects.first()
            context["field_list"] = [
                'order',
                'user',
                'role',
            ]
            return render(request, 'travel/reviewer_formset.html', context)


# TRIP #
########

class TripListView(TravelAccessRequiredMixin, FilterView):
    model = models.Conference
    filterset_class = filters.TripFilter
    template_name = 'travel/trip_list.html'
    queryset = models.Conference.objects.annotate(
        search_term=Concat(
            'name',
            Value(" "),
            'nom',
            Value(" "),
            'location',
            output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["h1"] = _("Trips")
        context["subtitle"] = _("Trips")
        context["crumbs"] = [
            {"title": _("Home"), "url": reverse("travel:index")},
            {"title": context["h1"]}
        ]
        context["paginate_by"] = 50
        context["new_url_name"] = "travel:trip_new"
        context["row_url_name"] = "travel:trip_detail"
        context["random_object"] = models.Conference.objects.first()
        context["field_list"] = [
            {"name": 'fiscal_year', "class": "", "width": "75px"},
            {"name": 'status', "class": "", },
            {"name": 'tname|{}'.format(_("Trip title")), "class": "", },
            {"name": 'location|{}'.format(_("location")), "class": "", },
            {"name": 'dates|{}'.format(_("dates")), "class": "", "width": "180px"},
            {"name": 'number_of_days|{}'.format(_("length (days)")), "class": "center-col", },
            {"name": 'is_adm_approval_required|{}'.format(_("ADM approval required?")), "class": "center-col", },
            {"name": 'total_travellers|{}'.format(_("Total travellers")), "class": "center-col", },
            {"name": 'connected_requests|{}'.format(_("Connected requests")), "class": "center-col", },
            {"name": 'verified_by', "class": "", },
        ]
        context["is_admin"] = in_travel_admin_group(self.request.user)
        return context


class TripDetailView(TravelAccessRequiredMixin, DetailView):
    model = models.Conference
    template_name = 'travel/trip_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["conf_field_list"] = conf_field_list
        context["reviewer_field_list"] = reviewer_field_list
        context["trip"] = self.get_object()

        context["h1"] = str(self.get_object())
        context["subtitle"] = context["h1"]
        context["crumbs"] = [
            {"title": _("Home"), "url": reverse("travel:index")},
            {"title": _("Trips"), "url": reverse("travel:trip_list")},
            {"title": context["h1"]}
        ]
        context["is_adm_admin"] = in_adm_admin_group(self.request.user)
        return context


class TripAdminNotesUpdateView(TravelADMAdminRequiredMixin, UpdateView):
    model = models.Conference
    form_class = forms.TripAdminNotesForm
    template_name = 'travel/generic_popout_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["h1"] = _("Administrative Notes (Public)")
        return context

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse("shared_models:close_me"))


class TripUpdateView(TravelAdminRequiredMixin, UpdateView):
    model = models.Conference
    form_class = forms.TripForm

    def get_template_names(self):
        return 'travel/trip_form_popout.html' if self.kwargs.get("pop") else 'travel/trip_form.html'

    def form_valid(self, form):
        my_object = form.save()

        # This is a bit tricky here. Right now will work with the assumption that we do not ever want to reset the reviewers unless
        # the trip was ADM approval required, and now is not, OR if it wasn't and now it is.
        if my_object.is_adm_approval_required and my_object.reviewers.count() == 0 or not my_object.is_adm_approval_required:
            # Add any trip reviewers to the trip, if adm approval is required.
            # This function will also delete any reviewers if adm approval is not required
            utils.get_trip_reviewers(my_object)

        if self.kwargs.get("pop"):
            return HttpResponseRedirect(reverse("shared_models:close_me"))
        else:
            return HttpResponseRedirect(reverse('travel:trip_detail', kwargs={'pk': my_object.id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()

        return context


class TripCreateView(TravelAccessRequiredMixin, CreateView):
    model = models.Conference
    form_class = forms.TripForm

    def get_template_names(self):
        if self.kwargs.get("pop"):
            return 'travel/trip_form_popout.html'
        else:
            return 'travel/trip_form.html'

    def get_success_url(self):
        if self.kwargs.get("pop"):
            return reverse("shared_models:close_me_no_refresh")
        else:
            return super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()

        return context

    def form_valid(self, form):
        my_object = form.save()

        # Add any trip reviewers to the trip, if adm approval is required
        utils.get_trip_reviewers(my_object)

        if self.kwargs.get("pop"):
            # create a new email object
            email = emails.NewTripEmail(my_object)
            # send the email object
            custom_send_mail(
                subject=email.subject,
                html_message=email.message,
                from_email=email.from_email,
                recipient_list=email.to_list
            )
            messages.success(self.request,
                             _("The trip has been added to the database!"))
        return super().form_valid(form)


class TripDeleteView(TravelAdminRequiredMixin, DeleteView):
    template_name = 'travel/trip_confirm_delete.html'
    model = models.Conference
    success_message = 'The trip was deleted successfully!'

    def get_success_url(self):
        if self.kwargs.get("back_to_verify"):
            adm = 1 if self.get_object().is_adm_approval_required else 0
            region = self.get_object().lead.id if adm == 0 else 0
            success_url = reverse_lazy('travel:admin_trip_verification_list', kwargs={"adm": adm, "region": region})
        else:
            success_url = reverse_lazy('travel:trip_list')
        return success_url

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class TripReviewProcessUpdateView(TravelADMAdminRequiredMixin, FormView):
    model = models.Conference
    form_class = forms.TripRequestApprovalForm
    template_name = 'travel/trip_review_process_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = models.Conference.objects.get(pk=self.kwargs.get("pk"))

        if my_object.status_id in [30, 41]:
            active_crumb = _("Start a Review")
            h1 = _("Do you wish to start a review on the following trip?")
            h2 = '<span class="blue-font">WARNING: starting a review on this trip will prevent any additional' \
                     ' travellers from adding themselves to it.</span>'
        else:
            active_crumb = _("End a Review")
            h1 = _("Do you wish to end a review on the following trip?")
            h2 = '<span class="red-font">WARNING: stopping the review on this trip will reset the' \
                 ' status of any exisitng recommendations and/or approvals.</span>'

        context["h1"] = h1
        context["h2"] = h2

        context["subtitle"] = active_crumb
        context["back_url"] = reverse("travel:trip_detail", kwargs={"pk": my_object.id})
        context["crumbs"] = [
            {"title": _("Home"), "url": reverse("travel:index")},
            {"title": _("Trips"), "url": reverse("travel:trip_list")},
            {"title": str(my_object), "url": context["back_url"]},
            {"title": active_crumb}
        ]

        context["trip"] = my_object
        context["conf_field_list"] = conf_field_list
        context['help_text_dict'] = get_help_text_dict()
        context["report_mode"] = True

        return context

    def form_valid(self, form):
        my_trip = models.Conference.objects.get(pk=self.kwargs.get("pk"))
        # figure out the current state of the request
        is_under_review = False if my_trip.status_id in [30,41] else True

        if is_under_review:
            utils.end_trip_review_process(my_trip)
        else:
            utils.start_trip_review_process(my_trip)
            # go and get approvals!!

        # No matter what business what done, we will call this function to sort through reviewer and request statuses
        utils.trip_approval_seeker(my_trip)
        my_trip.save()

        return HttpResponseRedirect(reverse("travel:trip_detail", kwargs={"pk": my_trip.id}))


class AdminTripVerificationListView(TravelAdminRequiredMixin, ListView):
    template_name = 'travel/trip_verification_list.html'

    def get_queryset(self):
        if self.kwargs.get("adm") == 1:
            queryset = models.Conference.objects.filter(status_id=30, is_adm_approval_required=True)
        else:
            queryset = models.Conference.objects.filter(
                status_id=30, lead_id=self.kwargs.get("region"), is_adm_approval_required=False
            )
        return queryset

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
        return context


class TripVerifyUpdateView(TravelAdminRequiredMixin, FormView):
    template_name = 'travel/trip_verification_form.html'
    model = models.Conference
    form_class = forms.TripRequestApprovalForm

    def test_func(self):
        my_trip = models.Conference.objects.get(pk=self.kwargs.get("pk"))
        if my_trip.is_adm_approval_required:
            return in_adm_admin_group(self.request.user)
        else:
            return in_travel_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("accounts:denied_access", kwargs={
                "message": _("Sorry, only ADMO administrators can verify projects that require ADM approval.")}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_trip = models.Conference.objects.get(pk=self.kwargs.get("pk"))
        context["object"] = my_trip
        context["conf_field_list"] = conf_field_list

        base_qs = models.Conference.objects.filter(~Q(id=my_trip.id)).filter(fiscal_year=my_trip.fiscal_year)

        context["same_day_trips"] = base_qs.filter(Q(start_date=my_trip.start_date) | Q(end_date=my_trip.end_date))

        context["same_location_trips"] = base_qs.filter(
            id__in=[trip.id for trip in base_qs if trip.location and my_trip.location and
                    utils.compare_strings(trip.location, my_trip.location) < 3]
        )

        similar_fr_name_trips = [trip.id for trip in base_qs if
                                 trip.nom and utils.compare_strings(trip.nom, trip.name) < 15] if my_trip.nom else []
        similar_en_name_trips = [trip.id for trip in base_qs if utils.compare_strings(trip.name, my_trip.name) < 15]
        my_list = list()
        my_list.extend(similar_en_name_trips)
        my_list.extend(similar_fr_name_trips)
        context["same_name_trips"] = base_qs.filter(
            id__in=set(my_list)
        )
        return context

    def form_valid(self, form):
        my_trip = models.Conference.objects.get(pk=self.kwargs.get("pk"))
        my_trip.status_id = 41
        my_trip.verified_by = self.request.user
        my_trip.save()
        return HttpResponseRedirect(reverse("travel:admin_trip_verification_list",
                                            kwargs={"region": self.kwargs.get("region"),
                                                    "adm": self.kwargs.get("adm")}))


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
        fy = nz(form.cleaned_data["fiscal_year"], "None")
        region = nz(form.cleaned_data["region"], "None")
        trip = nz(form.cleaned_data["trip"], "None")
        user = nz(form.cleaned_data["user"], "None")
        from_date = nz(form.cleaned_data["from_date"], "None")
        to_date = nz(form.cleaned_data["to_date"], "None")
        adm = nz(form.cleaned_data["adm"], "None")

        if report == 1:
            return HttpResponseRedirect(reverse("travel:export_cfts_list", kwargs={
                'fy': fy,
                'region': region,
                'trip': trip,
                'user': user,
                'from_date': from_date,
                'to_date': to_date,
            }))
        elif report == 2:
            email = form.cleaned_data["traveller"]
            return HttpResponseRedirect(reverse("travel:travel_plan", kwargs={
                'fy': fy,
                'email': email,
            }))

        elif report == 3:
            return HttpResponseRedirect(reverse("travel:export_trip_list", kwargs={
                'fy': fy,
                'region': region,
                'adm': adm,
                'from_date': from_date,
                'to_date': to_date,
            }))

        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("travel:report_search"))


@login_required()
def export_cfts_list(request, fy, region, trip, user, from_date, to_date):
    file_url = reports.generate_cfts_spreadsheet(fiscal_year=fy, region=region, trip=trip, user=user, from_date=from_date, to_date=to_date)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="CFTS export {}.xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


@login_required()
def export_trip_list(request, fy, region, adm, from_date, to_date):
    file_url = reports.generate_trip_list(fiscal_year=fy, region=region, adm=adm, from_date=from_date, to_date=to_date)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename="export of trips {timezone.now().strftime("%Y-%m-%d")}.xlsx"'
            return response
    raise Http404


@login_required()
def export_request_cfts(request, trip=None, trip_request=None):
    # print(trip)
    file_url = reports.generate_cfts_spreadsheet(trip_request=trip_request, trip=trip)
    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="CFTS export {}.xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


class TravelPlanPDF(TravelAccessRequiredMixin, PDFTemplateView):

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
        context["parent"] = my_object
        context["purpose_list"] = models.Purpose.objects.all()

        cost_categories = models.CostCategory.objects.all()
        my_dict = dict()

        # first, let's create an object list;
        if my_object.is_group_request:
            object_list = my_object.children_requests.filter(exclude_from_travel_plan=False)
        else:
            object_list = models.TripRequest.objects.filter(pk=my_object.id)

        my_dict["totals"] = dict()
        my_dict["totals"]["total"] = 0
        for obj in object_list:
            my_dict[obj] = dict()

            for cat in cost_categories:
                if not my_dict["totals"].get(cat):
                    my_dict["totals"][cat] = 0

                cat_amount = obj.trip_request_costs.filter(cost__cost_category=cat).values("amount_cad").order_by("amount_cad").aggregate(
                    dsum=Sum("amount_cad"))['dsum']
                my_dict[obj][cat] = cat_amount
                my_dict["totals"][cat] += nz(cat_amount, 0)
                my_dict["totals"]["total"] += nz(cat_amount, 0)

        # print(my_dict)
        context['object_list'] = object_list
        context['my_dict'] = my_dict
        # context['key_list'] = cost_categories
        return context


# SETTINGS #
############

@login_required(login_url='/accounts/login/')
@user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def delete_status(request, pk):
    my_obj = models.Status.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("travel:manage_statuses"))


@login_required(login_url='/accounts/login/')
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


@login_required(login_url='/accounts/login/')
@user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def delete_help_text(request, pk):
    my_obj = models.HelpText.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("travel:manage_help_text"))


@login_required(login_url='/accounts/login/')
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


@login_required(login_url='/accounts/login/')
@user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def delete_cost_category(request, pk):
    my_obj = models.CostCategory.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("travel:manage_cost_categories"))


@login_required(login_url='/accounts/login/')
@user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def manage_cost_categories(request):
    qs = models.CostCategory.objects.all()
    if request.method == 'POST':
        formset = forms.CostCategoryFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("travel:manage_cost_categories"))
    else:
        formset = forms.CostCategoryFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
        'order',
    ]
    context['title'] = "Manage Cost Categories"
    context['formset'] = formset
    return render(request, 'travel/manage_settings_small.html', context)


@login_required(login_url='/accounts/login/')
@user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def delete_cost(request, pk):
    my_obj = models.Cost.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("travel:manage_costs"))


@login_required(login_url='/accounts/login/')
@user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def manage_costs(request):
    qs = models.Cost.objects.all()
    if request.method == 'POST':
        formset = forms.CostFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("travel:manage_costs"))
    else:
        formset = forms.CostFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
        'cost_category',
    ]
    context['title'] = "Manage Costs"
    context['formset'] = formset
    return render(request, 'travel/manage_settings_small.html', context)


@login_required(login_url='/accounts/login/')
@user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def delete_njc_rate(request, pk):
    my_obj = models.NJCRates.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("travel:manage_njc_rates"))


@login_required(login_url='/accounts/login/')
@user_passes_test(in_travel_admin_group, login_url='/accounts/denied/')
def manage_njc_rates(request):
    qs = models.NJCRates.objects.all()
    if request.method == 'POST':
        formset = forms.NJCRatesFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("travel:manage_njc_rates"))
    else:
        formset = forms.NJCRatesFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'amount',
    ]
    context['title'] = "Manage NJC Rates"
    context['formset'] = formset
    return render(request, 'travel/manage_settings_small.html', context)


# Default Reviewer Settings

class DefaultReviewerListView(TravelAdminRequiredMixin, ListView):
    model = models.DefaultReviewer
    template_name = 'travel/default_reviewer_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'user',
            'sections',
            'branches',
            'reviewer_roles',
        ]
        context["random_object"] = self.object_list.first()
        return context


class DefaultReviewerUpdateView(TravelAdminRequiredMixin, UpdateView):
    model = models.DefaultReviewer
    form_class = forms.DefaultReviewerForm
    success_url = reverse_lazy('travel:default_reviewer_list')
    template_name = 'travel/default_reviewer_form.html'


class DefaultReviewerCreateView(TravelAdminRequiredMixin, CreateView):
    model = models.DefaultReviewer
    form_class = forms.DefaultReviewerForm
    success_url = reverse_lazy('travel:default_reviewer_list')
    template_name = 'travel/default_reviewer_form.html'


class DefaultReviewerDeleteView(TravelAdminRequiredMixin, DeleteView):
    model = models.DefaultReviewer
    success_url = reverse_lazy('travel:default_reviewer_list')
    success_message = 'The default reviewer was successfully deleted!'
    template_name = 'travel/default_reviewer_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


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


# TRAVEL REQUEST COST #
#######################


class TRCostCreateView(LoginRequiredMixin, CreateView):
    model = models.TripRequestCost
    template_name = 'travel/tr_cost_form_popout.html'
    form_class = forms.TripRequestCostForm

    def get_initial(self):
        my_trip_request = models.TripRequest.objects.get(pk=self.kwargs['trip_request'])
        return {
            'trip_request': my_trip_request,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_trip_request = models.TripRequest.objects.get(pk=self.kwargs['trip_request'])
        context['triprequest'] = my_trip_request
        return context

    def form_valid(self, form):
        my_object = form.save()
        if my_object.trip_request.trip:
            utils.manage_trip_warning(my_object.trip_request.trip)
        return HttpResponseRedirect(reverse('shared_models:close_me'))


class TRCostUpdateView(LoginRequiredMixin, UpdateView):
    model = models.TripRequestCost
    template_name = 'travel/tr_cost_form_popout.html'
    form_class = forms.TripRequestCostForm

    def form_valid(self, form):
        my_object = form.save()
        if my_object.trip_request.parent_request:
            my_trip = my_object.trip_request.parent_request.trip
        else:
            my_trip = my_object.trip_request.trip
        utils.manage_trip_warning(my_trip)

        return HttpResponseRedirect(reverse('shared_models:close_me_no_refresh'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def tr_cost_delete(request, pk):
    object = models.TripRequestCost.objects.get(pk=pk)
    if can_modify_request(request.user, object.trip_request.id):
        object.delete()
        messages.success(request, _("The cost has been successfully deleted."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect('/accounts/denied/')


def tr_cost_clear(request, trip_request):
    my_trip_request = models.TripRequest.objects.get(pk=trip_request)
    if can_modify_request(request.user, my_trip_request.id):
        utils.clear_empty_trip_request_costs(my_trip_request)
        messages.success(request, _("All empty costs have been cleared."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect('/accounts/denied/')


def tr_cost_populate(request, trip_request):
    my_trip_request = models.TripRequest.objects.get(pk=trip_request)
    if can_modify_request(request.user, my_trip_request.id):
        utils.populate_trip_request_costs(request, my_trip_request)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect('/accounts/denied/')
