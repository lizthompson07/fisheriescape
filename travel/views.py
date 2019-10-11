import json
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
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
        approval_count = models.Event.objects.filter(submitted__isnull=False).filter(
            Q(recommender_1=self.request.user) | Q(recommender_2=self.request.user) | Q(recommender_3=self.request.user) | Q(
                approver=self.request.user)).count()

        context["is_approver"] = True if approval_count > 0 else False

        return context


event_field_list = [
    'fiscal_year',
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
    'departure_location',
    'destination',
    'start_date',
    'end_date',

    # purpose
    'role',
    'reason',
    'purpose',
    'role_of_participant',
    'objective_of_event',
    'benefit_to_dfo',
    'multiple_conferences_rationale',
    'multiple_attendee_rationale',
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
    'approver_status|{}'.format(_("Expenditure Initiation")),
]


# EVENT #
#########
class EventListView(TravelAccessRequiredMixin, FilterView):
    model = models.Event
    filterset_class = filters.EventFilter
    template_name = 'travel/event_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Event.objects.first()
        context["field_list"] = [
            'fiscal_year',
            'section',
            'first_name',
            'last_name',
            'trip_title',
            'destination',
            'start_date',
            'end_date',
            'total_cost',
        ]
        return context


class EventApprovalListView(TravelAccessRequiredMixin, ListView):
    model = models.Event
    template_name = 'travel/event_approval_list.html'

    def get_queryset(self):
        qs = models.Event.objects.filter(submitted__isnull=False).filter(
            Q(recommender_1=self.request.user) | Q(recommender_2=self.request.user) | Q(recommender_3=self.request.user) | Q(
                approver=self.request.user))
        return qs.filter(waiting_on=self.request.user) if self.kwargs.get("which_ones") == "awaiting" else qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Event.objects.first()
        context["awaiting"] = True if self.kwargs.get("which_ones") else False
        context["field_list"] = [
            'first_name',
            'last_name',
            'trip_title',
            'destination',
            'start_date',
            'end_date',
            'total_cost',
            'recommender_1_status|{}'.format(_("Recommender 1 (status)")),
            'recommender_2_status|{}'.format(_("Recommender 2 (status)")),
            'recommender_3_status|{}'.format(_("Recommender 3 (status)")),
            'approver_status|{}'.format(_("Final Approval (status)")),
        ]
        return context


class EventDetailView(TravelAccessRequiredMixin, DetailView):
    model = models.Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = event_field_list
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

        # need to create a dictionary for sections and who the recommenders / appovers are
        section_dict = {}
        for section in shared_models.Section.objects.all():
            section_dict[section.id] = {}
            section_dict[section.id]["recommender_1"] = section.head_id
            section_dict[section.id]["recommender_2"] = section.division.head_id
            section_dict[section.id]["recommender_3"] = section.division.branch.head_id
            section_dict[section.id]["approver"] = section.division.branch.region.head_id
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
        context["field_list"] = event_field_list
        context["object"] = models.Event.objects.get(pk=self.kwargs.get("pk"))

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
                my_event.recommender_2 = None
                my_event.recommender_3 = None
                my_event.approver = None
                my_event.recommender_2_approval_status_id = 1
                my_event.recommender_3_approval_status_id = 1
                my_event.approver_approval_status_id = 1

        if my_event.recommender_2 == self.request.user:
            my_event.recommender_2_approval_date = timezone.now()
            if is_approved:
                my_event.recommender_2_approval_status_id = 2
            else:
                my_event.recommender_2_approval_status_id = 3
                my_event.recommender_3 = None
                my_event.approver = None
                my_event.recommender_3_approval_status_id = 1
                my_event.approver_approval_status_id = 1

        if my_event.recommender_3 == self.request.user:
            my_event.recommender_3_approval_date = timezone.now()
            if is_approved:
                my_event.recommender_3_approval_status_id = 2
            else:
                my_event.recommender_3_approval_status_id = 3
                my_event.approver = None
                my_event.approver_approval_status_id = 1

        if my_event.approver == self.request.user:
            my_event.approver_approval_date = timezone.now()
            if is_approved:
                my_event.approver_approval_status_id = 2
            else:
                my_event.approver_approval_status_id = 3

        my_event.save()
        return HttpResponseRedirect(reverse("travel:event_approval_list"))



class EventSubmitUpdateView(TravelAccessRequiredMixin, FormView):
    model = models.Event
    form_class = forms.EventApprovalForm
    template_name = 'travel/event_submission_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = event_field_list
        context["object"] = models.Event.objects.get(pk=self.kwargs.get("pk"))

        return context

    def form_valid(self, form):
        my_event = models.Event.objects.get(pk=self.kwargs.get("pk"))
        is_submitted = True if my_event.submitted else False
        if is_submitted:
            my_event.submitted = None
            # now clear all the reviewers
            my_event.recommender_1_approval_date = None
            my_event.recommender_1_approval_status_id = 1
            my_event.recommender_2_approval_date = None
            my_event.recommender_2_approval_status_id = 1
            my_event.recommender_3_approval_date = None
            my_event.recommender_3_approval_status_id = 1
            my_event.approver_approval_date = None
            my_event.approver_approval_status_id = 1

        else:
            my_event.submitted = timezone.now()
        my_event.save()
        return HttpResponseRedirect(reverse("travel:event_detail", kwargs={"pk":my_event.id}))


class EventCreateView(TravelAccessRequiredMixin, CreateView):
    model = models.Event
    form_class = forms.EventForm

    def get_initial(self):
        return {"user": self.request.user}

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
            section_dict[section.id]["approver"] = section.division.branch.region.head_id
        section_json = json.dumps(section_dict)
        # send JSON file to template so that it can be used by js script
        context['section_json'] = section_json
        return context


class EventDeleteView(TravelAccessRequiredMixin, DeleteView):
    model = models.Event
    success_url = reverse_lazy('travel:event_list')
    success_message = 'The event was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


def duplicate_event(request, pk):
    # get record to duplicate
    event = models.Event.objects.get(pk=pk)
    # remove the pk
    event.pk = None
    # save the record
    event.save()
    return HttpResponseRedirect(reverse("travel:event_edit", kwargs={"pk": event.id}))


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

        if report == 1:
            return HttpResponseRedirect(reverse("travel:export_cfts_list", kwargs={
                'fy': fy,
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
    file_url = reports.generate_cfts_spreadsheet(fy)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="custom master list export {}.xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


class TravelPlanPDF(TravelAccessRequiredMixin, PDFTemplateView):
    login_url = '/accounts/login_required/'
    template_name = "travel/travel_plan.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = models.Event.objects.filter(id=self.kwargs['pk'])
        context["object"] = object_list.first()
        context["object_list"] = object_list
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
