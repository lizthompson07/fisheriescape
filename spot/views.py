import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import TextField
from django.db.models.functions import Concat
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
###
from lib.functions.custom_functions import fiscal_year, listrify
from lib.functions.custom_functions import nz
from . import models
from . import forms
from . import filters
from . import emails
from . import reports


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'spot/close_me.html'


def in_spot_group(user):
    if user:
        return user.groups.filter(name='spot_access').count() != 0


class SpotAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

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
    model = models.Organization #ml_
    queryset = models.Organization.objects.annotate(
        search_term=Concat('name', 'id', output_field=TextField())) #ml_

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Organization.objects.first() #ml_
        context["field_list"] = [
            'name',
            #'abbrev',
            'province',
            #'grouping',
            #'regions',
        ]
        return context


#
class OrganizationDetailView(SpotAccessRequiredMixin, DetailView):
    template_name = 'spot/organization_detail.html'
    model = models.Organization #ml_

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'number',
            'name',
            'sub_organization',
            'address',
            'city',
            'postal_code',
            'province',
            'phone',
            'email',
            'website',
            'type',

            'date_last_modified',
            'last_modified_by',
        ]
        return context


class OrganizationUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/organization_form.html'
    model = models.Organization #ml_
    form_class = forms.OrganizationForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_org = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:org_detail", kwargs={"pk": my_org.id}))


class OrganizationCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/organization_form.html'
    model = models.Organization #ml_
    form_class = forms.OrganizationForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_org = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:org_detail", kwargs={"pk": my_org.id}))


class OrganizationDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/organization_confirm_delete.html'
    model = models.Organization #ml_
    success_url = reverse_lazy('spot:org_list')
    success_message = 'The organization was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# MEMBER  (ORGANIZATION MEMBER) #
#################################
class MemberCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.OrganizationMember #ml_
    template_name = 'spot/member_form_popout.html'

    form_class = forms.MemberForm

    def get_initial(self):
        org = models.Organization.objects.get(pk=self.kwargs['org']) #ml_
        return {
            'organization': org,
            'last_modified_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = models.Organization.objects.get(id=self.kwargs['org']) #ml_
        context['organization'] = org

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in models.Person.objects.all() #ml_
        ]

        context['person_list'] = person_list

        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))


class MemberUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.OrganizationMember #ml_
    template_name = 'spot/member_form_popout.html'
    form_class = forms.MemberForm


    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in models.Person.objects.all() #ml_
        ]

        context['person_list'] = person_list

        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class MemberDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/member_confirm_delete.html'
    model = models.OrganizationMember #ml_
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
    model = models.Person #ml_
    queryset = models.Person.objects.annotate(
        search_term=Concat('first_name', 'last_name', 'id', output_field=TextField())) #ml_

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Person.objects.first() #ml_
        context["field_list"] = [
            'display_name|Last name, First name',
            'phone',
            'email',
            'organizations',
        ]
        return context


class PersonDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Person #ml_
    template_name = 'spot/person_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'first_name',
            'last_name',
            'phone',
            'email',
            'organizations',
            'section',
            'role',
            'other_membership',
            'last_modified_by',
        ]
        return context


class PersonUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.Person #ml_
    template_name = 'spot/person_form.html'
    form_class = forms.PersonForm

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("spot:person_detail", kwargs={"pk": self.kwargs["pk"]})


class PersonUpdateViewPopout(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/person_form_popout.html'
    model = models.Person #ml_
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
    model = models.Person #ml_
    form_class = forms.NewPersonForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_person = form.save()
        my_org = models.Organization.objects.get(pk=form.cleaned_data["organization"]) #ml_
        print(my_org)
        my_role = form.cleaned_data["role"]
        my_new_member = models.OrganizationMember.objects.create(
            person=my_person,
            organization=my_org,
            role=my_role
        ) #ml
        my_new_member.save()
        return HttpResponseRedirect(reverse_lazy("spot:person_detail", kwargs={"pk": my_person.id}))


class PersonCreateViewPopout(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/person_form_popout.html'
    model = models.Person #ml_
    form_class = forms.NewPersonForm

    def form_valid(self, form):
        my_person = form.save()
        my_org = models.Organization.objects.get(pk=form.cleaned_data["organization"]) #ml_
        print(my_org)
        my_role = form.cleaned_data["role"]
        my_new_member = models.OrganizationMember.objects.create(
            person=my_person,
            organization=my_org,
            role=my_role
        ) #ml_
        my_new_member.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class PersonDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/person_confirm_delete.html'
    model = models.Person
    success_url = reverse_lazy('spot:person_list')
    success_message = 'The person was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# PROJECT #
###########

class ProjectListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/project_list.html'
    filterset_class = filters.ProjectFilter
    model = models.Project
    queryset = models.Project.objects.annotate(
        search_term=Concat('id', 'title', 'title_abbrev', 'program_reference_number', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["my_object"] = models.Project.objects.first()
        context["field_list"] = [
            'id',
            'path_number',
            'program_reference_number',
            'status',
            'start_year',
            'program.abbrev_eng',
            'organization',
            'title',
            'project_length',
            'regions',
        ]
        return context


class ProjectDetailView(SpotAccessRequiredMixin, DetailView):
    template_name = 'spot/project_detail.html'
    model = models.Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        context["current_fy"] = fiscal_year()
        context["field_list"] = [
            'id',
            'path_number',
            'program_reference_number',
            'organization',
            'title',
            'program',
            'language',
            'status',
            'regions',
            'start_year',
            'project_length',
            'activities',
            'watersheds',
            'spp',
            'date_completed',
            'summary',
        ]

        site_list = [["{} ({})".format(obj.name, obj.site_type), obj.lat, obj.long] for obj in self.object.sites.all() if
                     obj.lat and obj.long]
        context['site_list'] = site_list

        return context


class ProjectUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/project_form.html'
    model = models.Project
    form_class = forms.ProjectForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_project = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:project_detail", kwargs={"pk": my_project.id}))


class ProjectCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/project_form.html'
    model = models.Project
    form_class = forms.NewProjectForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_project = form.save()

        # # add a project year
        # my_start_year = models.ProjectYear.objects.create(
        #     project=my_project,
        #     fiscal_year=my_project.start_year,
        # )
        # my_start_year.save()
        return HttpResponseRedirect(reverse_lazy("spot:project_detail", kwargs={"pk": my_project.id}))


class ProjectDeleteView(SpotAdminRequiredMixin, DeleteView):
    template_name = 'spot/project_confirm_delete.html'
    model = models.Project
    success_url = reverse_lazy('spot:project_list')
    success_message = 'The project was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# PROJECT PERSON #
##################
class ProjectPersonCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.ProjectPerson
    template_name = 'spot/project_person_form_popout.html'

    form_class = forms.ProjectPersonForm

    def get_initial(self):
        my_project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': my_project,
            'last_modified_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_project = models.Project.objects.get(pk=self.kwargs['project'])
        context['project'] = my_project

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in models.Person.objects.all() #ml_
        ]

        # get a list of all site users who have not already been connected to ml_models.Person
        person_list_1 = [
            '<a href="#" class="user_insert purple-font" url="{my_url}">{first} {last} (SITE USER)</a>'.format(
                my_url=reverse("spot:user_to_person", kwargs={
                    "user": u.id,
                    "view_name": "project_person_new",
                    "pk": my_project.id,
                }),
                first=u.first_name,
                last=u.last_name,
            ) for u in User.objects.all() if
            u.id not in [p.connected_user_id for p in models.Person.objects.filter(connected_user__isnull=False)]
        ] #ml_
        person_list.extend(person_list_1)
        context['person_list'] = person_list

        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))


class ProjectPersonUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.ProjectPerson
    template_name = 'spot/project_person_form_popout.html'
    form_class = forms.ProjectPersonForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in models.Person.objects.all() #ml_
        ]

        # get a list of all site users who have not already been connected to ml_models.Person
        person_list_1 = [
            '<a href="#" class="user_insert purple-font" url="{my_url}">{first} {last} (SITE USER)</a>'.format(
                my_url=reverse("spot:user_to_person", kwargs={
                    "user": u.id,
                    "view_name": "project_person_edit",
                    "pk": context['object'].id,
                }),
                first=u.first_name,
                last=u.last_name,
            ) for u in User.objects.all() if
            u.id not in [p.connected_user_id for p in models.Person.objects.filter(connected_user__isnull=False)]
        ] #ml_
        person_list.extend(person_list_1)
        context['person_list'] = person_list
        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class ProjectPersonDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/project_person_confirm_delete.html'
    model = models.ProjectPerson
    success_url = reverse_lazy('spot:close_me')
    success_message = 'This contact was successfully removed!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


def user_to_person(request, user, view_name, pk):
    """
    Adds a user to the masterlist person table
    :param request: HTTP request
    :param user: pk of site user
    :param view_name: should be either 'project_person_new' or 'project_person_edit'
    :param pk: could be pk of project or project person, depending on which view is being called from
    :return: HTTP response
    """
    my_user = User.objects.get(pk=user)
    my_new_person = models.Person.objects.create(
        first_name=my_user.first_name,
        last_name=my_user.last_name,
        connected_user=my_user,
    ) #ml_
    my_new_person.save()

    # figure out where to go!
    if view_name == "project_person_new":
        target_url = reverse("spot:" + view_name, kwargs={"project": pk})

    elif view_name == "project_person_edit":
        target_url = reverse("spot:" + view_name, kwargs={"pk": pk})

    else:
        target_url = reverse("spot:close_me")

    return HttpResponseRedirect(target_url)


class ObjectiveListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/objective_list.html'
    #filterset NEED TO DO
    model = models.Objective
    queryset = models.Objective.objects.annotate()
    search_term = Concat('number', 'id', output_field=TextField())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Objective.objects.first()
        context["field_list"] = [
            'number',
            'key_element',
            'activity',
            'location',
        ]
        return context


class ObjectiveDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Objective
    template_name = 'spot/objective_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'number',
            'work_plan_section',
            'task_description',
            'key_element',
            'activity',
            'element_title',
            'activity_title',
            'pst_requirement',
            'location',
            'objective_category',
            'duration',
            'species',
            'target_sample_number',
            'sample_type',
            'salmon_stage',
            'sil_requirement',
            'expected_results',
            'scientific_outcome',
            'outcomes_category',
            'outcomes_deadline',
            'outcomes_contact',
            'data_quality_type',
            'data_quality_level',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class ObjectiveUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/objective_form.html'
    model = models.Objective
    form_class = forms.ObjectiveForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_obj = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:obj_detail", kwargs={"pk": my_obj.id}))


class ObjectiveCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/objective_form.html'
    model = models.Objective
    form_class = forms.ObjectiveForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_obj = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:obj_detail", kwargs={"pk": my_obj.id}))


class ObjectiveDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/objective_confirm_delete.html'
    model = models.Objective
    success_url = reverse_lazy('spot:obj_list')
    success_message = 'The objective was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class MethodListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/method_list.html'
    #filterset NEED TO DO
    model = models.Method
    queryset = models.Method.objects.annotate()
    search_term = Concat('doc_num', 'id', output_field=TextField())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Method.objects.first()
        context["field_list"] = [
            'document_number',
            'document_category',
            'document_topic',
        ]
        return context


class MethodDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Method
    template_name = 'spot/method_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'document_number',
            'document_category',
            'authors',
            'publication_year',
            'title',
            'reference_number',
            'publisher',
            'document_link',
            'database',
            'method_category',
            'method_type',
            'form_name',
            'region',
            'form_category',
            'form_link',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class MethodUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/method_form.html'
    model = models.Method
    form_class = forms.MethodForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_meth = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:meth_detail", kwargs={"pk": my_meth.id}))


class MethodCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/method_form.html'
    model = models.Method
    form_class = forms.MethodForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_meth = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:meth_detail", kwargs={"pk": my_meth.id}))


class MethodDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/method_confirm_delete.html'
    model = models.Method
    success_url = reverse_lazy('spot:meth_list')
    success_message = 'The Method was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class DatabasesUsedListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/database_list.html'
    #filterset NEED TO DO
    model = models.DatabasesUsed
    queryset = models.DatabasesUsed.objects.annotate()
    search_term = Concat('database', 'id', output_field=TextField())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.DatabasesUsed.objects.first()
        context["field_list"] = [
            'database',
            'analysis_program',
            'models_used',
        ]
        return context


class DatabasesUsedDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.DatabasesUsed
    template_name = 'spot/database_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'database',
            'analysis_program',
            'models_used',
            'data_format',
            'data_fn',
            'data_DFO',
            'data_quality',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class DatabasesUsedUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/database_form.html'
    model = models.DatabasesUsed
    form_class = forms.DatabasesUsedForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_data = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:data_detail", kwargs={"pk": my_data.id}))


class DatabasesUsedCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/database_form.html'
    model = models.DatabasesUsed
    form_class = forms.DatabasesUsedForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_data = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:data_detail", kwargs={"pk": my_data.id}))


class DatabasesUsedDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/database_confirm_delete.html'
    model = models.DatabasesUsed
    success_url = reverse_lazy('spot:data_list')
    success_message = 'The Database was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)






# PROJECT YEAR #
################

"""

class ProjectYearDetailView(SpotAccessRequiredMixin, DetailView):
    template_name = 'spot/project_year_detail.html'
    model = models.ProjectYear

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_fy"] = fiscal_year()
        # send in the name of the project's first fiscal year
        context["first_year"] = context["object"].project.years.first().fiscal_year.full
        # currently field are being called manually into a table. This can be improved when time permits
        context["field_list"] = [
            'annual_funding',
        ]
        context["my_payment"] = models.Payment.objects.first()
        context["payment_field_list"] = [
            # 'project_year',
            'claim_number',
            'disbursement|Total amount',
            'from_period',
            'to_period',
            'final_payment',
            'materials_submitted',
            'nhq_notified',
            'payment_confirmed',
            'notes',
        ]
        return context


class ProjectYearUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/project_year_form.html'
    model = models.ProjectYear
    form_class = forms.ProjectYearForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:year_detail", kwargs={"pk": my_object.id}))


class ProjectYearCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/project_year_form.html'
    model = models.ProjectYear
    form_class = forms.ProjectYearForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_project = models.Project.objects.get(pk=self.kwargs['project'])
        context['project'] = my_project
        return context

    def get_initial(self):
        my_project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': my_project,
            'last_modified_by': self.request.user,
        }

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:year_detail", kwargs={"pk": my_object.id}))


class ProjectYearDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/project_year_confirm_delete.html'
    model = models.ProjectYear
    success_message = 'The project year was deleted successfully!'

    def get_success_url(self):
        my_project = models.ProjectYear.objects.get(pk=self.kwargs['pk']).project
        return reverse_lazy('spot:project_detail', kwargs={"pk": my_project.id})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# TRACKING #
############


class TrackingUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/tracking_form_popout.html'

    def get_queryset(self, *args, **kwargs):
        if self.kwargs["step"] == "initiation" or self.kwargs["step"] == "review" or self.kwargs["step"] == "negotiations" or self.kwargs[
            "step"] == "ca-admin" or self.kwargs["step"] == "attributes":
            return models.Project.objects.all()
        elif self.kwargs["step"] == "my-update":
            return models.ProjectYear.objects.all()
        else:
            return None

    def get_form_class(self, *args, **kwargs):
        if self.kwargs["step"] == "initiation":
            return forms.InitiationForm
        elif self.kwargs["step"] == "review":
            return forms.ProjectReviewForm
        elif self.kwargs["step"] == "negotiations":
            return forms.NegotiationForm
        elif self.kwargs["step"] == "ca-admin":
            return forms.CAAdministrationForm
        elif self.kwargs["step"] == "attributes":
            return forms.AttributesForm
        else:
            return forms.ProjectYearForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_object = models.Project.objects.get(pk=self.kwargs["pk"])
        step_name = self.kwargs["step"]
        if step_name == "initiation":
            step_name = "Initiation"
            context["email"] = emails.MasterEmail(my_object, "eoi_acknowledgement", self.request)
        elif step_name == "review":
            step_name = "Regional Review"
        elif step_name == "negotiations":
            step_name = "Negotiations"
            context["email"] = emails.MasterEmail(my_object, "negotiations", self.request)
        elif step_name == "ca-admin":
            step_name = "CA Administration"
        elif step_name == "attributes":
            step_name = "Project Attributes"
        context["step_name"] = step_name
        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }

    def form_valid(self, form):
        my_object = form.save()

        # if we are at the review step
        if self.kwargs["step"] == "review":
            # if there is recommended funding
            if my_object.recommended_funding_y1:
                my_year, created = models.ProjectYear.objects.get_or_create(project=my_object, fiscal_year=my_object.start_year)
                if created:
                    my_year.annual_funding = my_object.recommended_funding_y1
                    my_year.save()
            if my_object.recommended_funding_y2:
                my_year, created = models.ProjectYear.objects.get_or_create(project=my_object, fiscal_year_id=my_object.start_year_id + 1)
                if created:
                    my_year.annual_funding = my_object.recommended_funding_y2
                    my_year.save()
            if my_object.recommended_funding_y3:
                my_year, created = models.ProjectYear.objects.get_or_create(project=my_object, fiscal_year_id=my_object.start_year_id + 2)
                if created:
                    my_year.annual_funding = my_object.recommended_funding_y3
                    my_year.save()
            if my_object.recommended_funding_y4:
                my_year, created = models.ProjectYear.objects.get_or_create(project=my_object, fiscal_year_id=my_object.start_year_id + 3)
                if created:
                    my_year.annual_funding = my_object.recommended_funding_y4
                    my_year.save()
            if my_object.recommended_funding_y5:
                my_year, created = models.ProjectYear.objects.get_or_create(project=my_object, fiscal_year_id=my_object.start_year_id + 4)
                if created:
                    my_year.annual_funding = my_object.recommended_funding_y5
                    my_year.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))


class EOIUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/tracking_form_popout.html'
    form_class = forms.EOIForm

    def get_object(self, *args, **kwargs):
        my_eoi, created = models.ExpressionOfInterest.objects.get_or_create(
            project=models.Project.objects.get(pk=self.kwargs["pk"])
        )
        if created:
            my_eoi.save()
        return my_eoi

    def get_initial(self):
        return {
            'project': models.Project.objects.get(pk=self.kwargs["pk"]),
            'last_modified_by': self.request.user,
        }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["step_name"] = "EOI"
        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))


class CAChecklistUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/tracking_form_popout.html'
    form_class = forms.CAChecklistForm

    def get_object(self, *args, **kwargs):
        my_ca_checklist, created = models.ContributionAgreementChecklist.objects.get_or_create(
            project=models.Project.objects.get(pk=self.kwargs["pk"])
        )
        if created:
            my_ca_checklist.save()
        return my_ca_checklist

    def get_initial(self):
        return {
            'project': models.Project.objects.get(pk=self.kwargs["pk"]),
            'last_modified_by': self.request.user,
        }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["step_name"] = "CA Checklist"
        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))


# PAYMENT #
################
class PaymentUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/payment_form_popout.html'
    model = models.Payment
    form_class = forms.PaymentForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))


class PaymentCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/payment_form_popout.html'
    model = models.Payment
    form_class = forms.PaymentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_project_year = models.ProjectYear.objects.get(pk=self.kwargs['project_year'])
        context['project_year'] = my_project_year
        return context

    def get_initial(self):
        my_project_year = models.ProjectYear.objects.get(pk=self.kwargs['project_year'])
        if my_project_year.payments.count() == 0:
            claim_number = 1
        else:
            claim_number = my_project_year.payments.count() + 1
        return {
            'project_year': my_project_year,
            'last_modified_by': self.request.user,
            'claim_number': claim_number,
        }

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))


class PaymentDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/payment_confirm_delete.html'
    model = models.Payment
    success_message = 'The payment was deleted successfully!'

    def get_success_url(self):
        return reverse_lazy('spot:close_me')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# FILE #
########

class FileCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.File
    template_name = 'spot/file_form_popout.html'
    form_class = forms.FileForm
    success_url = reverse_lazy('spot:close_me')

    def get_initial(self):
        super().get_initial()
        my_project = models.Project.objects.get(pk=self.kwargs['project'])
        my_dict = {
            'project': my_project,
            'uploaded_by': self.request.user,
        }
        if self.kwargs.get("type"):
            my_dict['file_type'] = models.FileType.objects.get(pk=self.kwargs.get("type"))
        return my_dict

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_project = models.Project.objects.get(id=self.kwargs['project'])
        context['project'] = my_project
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))


class FileUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.File
    template_name = 'spot/file_form_popout.html'
    form_class = forms.FileForm


    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))

    def get_initial(self):
        return {
            'date_modified': timezone.now(),
            'uploaded_by': self.request.user,
        }


class FileDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/file_confirm_delete.html'
    model = models.File
    success_message = 'The file was deleted successfully!'

    def get_success_url(self):
        return reverse_lazy('spot:close_me')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# SITE #
########
class SiteCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.Site
    template_name = 'spot/site_form_popout.html'

    form_class = forms.SiteForm

    def get_initial(self):
        my_project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': my_project,
            'last_modified_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_project = models.Project.objects.get(pk=self.kwargs['project'])
        context['project'] = my_project
        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))


class SiteUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.Site
    template_name = 'spot/site_form_popout.html'
    form_class = forms.SiteForm


    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class SiteDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/site_confirm_delete.html'
    model = models.Site
    success_url = reverse_lazy('spot:close_me')
    success_message = 'The site was successfully removed!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# REPORTS #
###########

class ReportSearchFormView(SpotAccessRequiredMixin, FormView):
    template_name = 'spot/report_search.html'
    form_class = forms.ReportSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        fiscal_year = str(form.cleaned_data["fiscal_year"])
        report = int(form.cleaned_data["report"])
        programs = listrify(form.cleaned_data["programs"])

        if programs == "":
            sections = "None"

        if report == 1:
            return HttpResponseRedirect(reverse("projects:report_neg", kwargs={
                'fy': fiscal_year,
                'programs': programs,
            }))
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("ihub:report_search"))


class NegotiationReport(SpotAccessRequiredMixin, TemplateView):
    template_name = 'masterlist/report_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        fiscal_year = str(form.cleaned_data["fiscal_year"])
        report = int(form.cleaned_data["report"])
        programs = listrify(form.cleaned_data["programs"])

        if programs == "":
            sections = "None"

        if report == 1:
            return HttpResponseRedirect(reverse("projects:report_neg", kwargs={
                'fy': fiscal_year,
                'programs': programs,
            }))
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("ihub:report_search"))


# SETTINGS #
############
@login_required(login_url='/accounts/login/')
@user_passes_test(in_spot_admin_group, login_url='/accounts/denied/')
def manage_activities(request):
    qs = models.Activity.objects.all()
    if request.method == 'POST':
        formset = forms.ActivityFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Activities have been successfully updated")
            return HttpResponseRedirect(reverse("spot:manage_activities"))
    else:
        formset = forms.ActivityFormSet(
            queryset=qs)
    context = {}
    context['title'] = "Manage Activities"
    context['formset'] = formset
    context["my_object"] = qs.first()
    context["field_list"] = [
        'program',
        'name',
        'nom',
        'habitat',
        'category_eng',
        'category_fre',
    ]
    return render(request, 'spot/manage_settings_small.html', context)


@login_required(login_url='/accounts/login/')
@user_passes_test(in_spot_admin_group, login_url='/accounts/denied/')
def delete_activity(request, pk):
    my_obj = models.Activity.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("spot:manage_activities"))


@login_required(login_url='/accounts/login/')
@user_passes_test(in_spot_admin_group, login_url='/accounts/denied/')
def manage_watersheds(request):
    qs = models.Watershed.objects.all()
    if request.method == 'POST':
        formset = forms.WatershedFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Watersheds have been successfully updated")
            return HttpResponseRedirect(reverse("spot:manage_watersheds"))
    else:
        formset = forms.WatershedFormSet(
            queryset=qs)
    context = {}
    context['title'] = "Manage Watersheds"
    context['formset'] = formset
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
        'province',
        'drainage_basin',
        'notes',
    ]
    return render(request, 'spot/manage_settings_small.html', context)


@login_required(login_url='/accounts/login/')
@user_passes_test(in_spot_admin_group, login_url='/accounts/denied/')
def delete_watershed(request, pk):
    my_obj = models.Watershed.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("spot:manage_watersheds"))


@login_required(login_url='/accounts/login/')
@user_passes_test(in_spot_admin_group, login_url='/accounts/denied/')
def manage_basins(request):
    qs = models.DrainageBasin.objects.all()
    if request.method == 'POST':
        formset = forms.DrainageBasinFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Drainage Basins have been successfully updated")
            return HttpResponseRedirect(reverse("spot:manage_basins"))
    else:
        formset = forms.DrainageBasinFormSet(
            queryset=qs)
    context = {}
    context['title'] = "Manage Drainage Basins"
    context['formset'] = formset
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
    ]
    return render(request, 'spot/manage_settings_small.html', context)


@login_required(login_url='/accounts/login/')
@user_passes_test(in_spot_admin_group, login_url='/accounts/denied/')
def delete_basin(request, pk):
    my_obj = models.DrainageBasin.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("spot:manage_basins"))
"""


