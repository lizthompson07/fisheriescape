import os
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import TextField
from django.db.models.functions import Concat
from django.utils import timezone
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
###

from lib.functions.nz import nz
from . import models
from . import forms
from . import filters
from . import reports
from masterlist import models as ml_models


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'spot/close_me.html'


def in_spot_group(user):
    if user:
        return user.groups.filter(name='spot_access').count() != 0


class SpotAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_spot_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


def in_spot_admin_group(user):
    if user:
        return user.groups.filter(name='spot_admin').count() != 0


class SpotAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_spot_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class IndexTemplateView(SpotAccessRequiredMixin, TemplateView):
    template_name = 'spot/index.html'

# ORGANIZATION #
################

class OrganizationListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/organization_list.html'
    filterset_class = filters.OrganizationFilter
    model = ml_models.Organization
    queryset = ml_models.Organization.objects.annotate(
        search_term=Concat('name_eng', 'name_fre', 'abbrev', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = ml_models.Organization.objects.first()
        context["field_list"] = [
            'name_eng',
            'abbrev',
            'province',
            'grouping',
            'regions',
        ]
        return context

#
class OrganizationDetailView(SpotAccessRequiredMixin, DetailView):
    template_name = 'spot/organization_detail.html'
    model = ml_models.Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name_eng',
            'abbrev',
            'address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
            'dfo_contact_instructions',
            'notes',
            'grouping',
            'regions',
            'sectors',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class OrganizationUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/organization_form.html'
    model = ml_models.Organization
    form_class = forms.OrganizationForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class OrganizationCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/organization_form.html'
    model = ml_models.Organization
    form_class = forms.OrganizationForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class OrganizationDeleteView(SpotAdminRequiredMixin, DeleteView):
    template_name = 'spot/organization_confirm_delete.html'
    model = ml_models.Organization
    success_url = reverse_lazy('spot:org_list')
    success_message = 'The organization was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# MEMBER  (ORGANIZATION MEMBER) #
#################################
class MemberCreateView(SpotAccessRequiredMixin, CreateView):
    model = ml_models.OrganizationMember
    template_name = 'spot/member_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.NewMemberForm

    def get_initial(self):
        org = ml_models.Organization.objects.get(pk=self.kwargs['org'])
        return {
            'organization': org,
            'last_modified_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = ml_models.Organization.objects.get(id=self.kwargs['org'])
        context['organization'] = org

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in ml_models.Person.objects.all()
        ]

        context['person_list'] = person_list

        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))


class MemberUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = ml_models.OrganizationMember
    template_name = 'spot/member_form_popout.html'
    form_class = forms.MemberForm
    login_url = '/accounts/login_required/'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in ml_models.Person.objects.all()
        ]

        context['person_list'] = person_list

        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class MemberDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/member_confirm_delete.html'
    model = ml_models.OrganizationMember
    success_url = reverse_lazy('spot:close_me')
    success_message = 'This member was successfully removed!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# PERSON #
##########

class PersonListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/person_list.html'
    filterset_class = filters.PersonFilter
    model = ml_models.Person
    queryset = ml_models.Person.objects.annotate(
        search_term=Concat('first_name', 'last_name', 'notes', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = ml_models.Person.objects.first()
        context["field_list"] = [
            'last_name',
            'first_name',
            'phone_1',
            'phone_2',
            'email_1',
        ]
        return context


class PersonDetailView(SpotAccessRequiredMixin, DetailView):
    model = ml_models.Person

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'first_name',
            'last_name',
            'phone_1',
            'phone_2',
            'fax',
            'email_1',
            'email_2',
            'notes',
            'last_modified_by',
        ]
        return context



class PersonUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = ml_models.Person
    form_class = forms.PersonForm

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }


class PersonUpdateViewPopout(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/person_form_popout.html'
    model = ml_models.Person
    form_class = forms.PersonForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }

class PersonCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/person_form.html'
    model = ml_models.Person
    form_class = forms.PersonForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class PersonCreateViewPopout(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/person_form_popout.html'
    model = ml_models.Person
    form_class = forms.PersonForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class PersonDeleteView(SpotAdminRequiredMixin, DeleteView):
    template_name = 'spot/person_confirm_delete.html'
    model = ml_models.Person
    success_url = reverse_lazy('spot:person_list')
    success_message = 'The person was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)





# # CONSULTATION INSTRUCTION #
# ############################
#
# class InstructionCreateView(SpotAccessRequiredMixin, CreateView):
#     model = models.ConsultationInstruction
#     template_name = 'spot/instruction_form.html'
#     form_class = forms.InstructionForm
#
#     def get_initial(self):
#         org = models.Organization.objects.get(pk=self.kwargs['org'])
#         return {
#             'organization': org,
#             'last_modified_by': self.request.user
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         org = models.Organization.objects.get(id=self.kwargs['org'])
#         context['org'] = org
#
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse_lazy('spot:instruction_edit', kwargs={"pk":object.id}))
#
#
# class InstructionUpdateView(SpotAccessRequiredMixin, UpdateView):
#     model = models.ConsultationInstruction
#     template_name = 'spot/instruction_form.html'
#     form_class = forms.InstructionForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # # get a list of members from only the indigenous organizations
#         member_list = ['<a href="#" class="add-btn" target-url="{target_url}">{text}</a>'.format(
#             target_url=reverse_lazy("spot:recipient_new", kwargs={"instruction": self.object.id, "member": member.id}),
#             text=member) for member in models.OrganizationMember.objects.filter(organization__grouping__is_indigenous=True)]
#         context['member_list'] = member_list
#
#         return context
#
#     def get_initial(self):
#         return {
#             'last_modified_by': self.request.user
#         }
#
#
# class InstructionDeleteView(SpotAdminRequiredMixin, DeleteView):
#     model = models.ConsultationInstruction
#     success_message = _("The organization's consultation instructions were deleted successfully!")
#     template_name = 'spot/instruction_confirm_delete.html'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
#
#     def get_success_url(self):
#         return reverse_lazy("spot:org_detail", kwargs={"pk": self.object.organization.id})
#
#
# # RECIPIENTS #
# ##############
#
# class RecipientCreateView(SpotAdminRequiredMixin, CreateView):
#     model = models.ConsultationInstructionRecipient
#     template_name = 'spot/recipient_form_popout.html'
#     login_url = '/accounts/login_required/'
#     form_class = forms.RecipientForm
#
#     def get_initial(self):
#         instruction = models.ConsultationInstruction.objects.get(pk=self.kwargs['instruction'])
#         member = models.OrganizationMember.objects.get(pk=self.kwargs['member'])
#         return {
#             'consultation_instruction': instruction.id,
#             'member': member.id,
#             'last_modified_by': self.request.user,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         instruction = models.ConsultationInstruction.objects.get(id=self.kwargs['instruction'])
#         member = models.OrganizationMember.objects.get(id=self.kwargs['member'])
#         context['instruction'] = instruction
#         context['member'] = member
#         return context
#
#     def form_valid(self, form):
#         self.object = form.save()
#         return HttpResponseRedirect(reverse('spot:close_me'))
#
#
# class RecipientUpdateView(SpotAdminRequiredMixin, UpdateView):
#     model = models.ConsultationInstructionRecipient
#     template_name = 'spot/recipient_form_popout.html'
#     form_class = forms.RecipientForm
#
#     def form_valid(self, form):
#         self.object = form.save()
#         return HttpResponseRedirect(reverse('spot:close_me'))
#
#     def get_initial(self):
#         return {
#             'last_modified_by': self.request.user,
#         }
#
#
# def recipient_delete(request, pk):
#     object = models.ConsultationInstructionRecipient.objects.get(pk=pk)
#     object.delete()
#     messages.success(request, "The recipient has been successfully deleted from {}.".format(object.consultation_instruction))
#     return HttpResponseRedirect(reverse_lazy("spot:instruction_edit", kwargs={"pk": object.consultation_instruction.id}))
#
#
# # REPORTS #
# ###########
#
# class ReportSearchFormView(SpotAccessRequiredMixin, FormView):
#     template_name = 'spot/report_search.html'
#     form_class = forms.ReportSearchForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context
#
#     def form_valid(self, form):
#         report = int(form.cleaned_data["report"])
#         provinces = str(form.cleaned_data["provinces"]).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")
#         groupings = str(form.cleaned_data["groupings"]).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")
#         sectors = str(form.cleaned_data["sectors"]).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")
#         regions = str(form.cleaned_data["regions"]).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")
#         is_indigenous = int(form.cleaned_data["is_indigenous"])
#         species = str(form.cleaned_data["species"])
#
#         if provinces == "":
#             provinces = "None"
#         if groupings == "":
#             groupings = "None"
#         if sectors == "":
#             sectors = "None"
#         if regions == "":
#             regions = "None"
#         if species == "":
#             species = "None"
#
#         if report == 1:
#             return HttpResponseRedirect(reverse("spot:export_custom_list", kwargs={
#                 'provinces': provinces,
#                 'groupings': groupings,
#                 'sectors': sectors,
#                 'regions': regions,
#                 'is_indigenous': is_indigenous,
#                 'species': species,
#             }))
#
#         else:
#             messages.error(self.request, "Report is not available. Please select another report.")
#             return HttpResponseRedirect(reverse("spot:report_search"))
#
#
# def export_custom_list(request, provinces, groupings, sectors, regions, is_indigenous, species):
#     file_url = reports.generate_custom_list(provinces, groupings, sectors, regions, is_indigenous, species)
#
#     if os.path.exists(file_url):
#         with open(file_url, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
#             response['Content-Disposition'] = 'inline; filename="custom master list export {}.xlsx"'.format(
#                 timezone.now().strftime("%Y-%m-%d"))
#             return response
#     raise Http404
