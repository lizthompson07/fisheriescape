import json
import os
###
from collections import OrderedDict
from copy import deepcopy

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Value, TextField, Q, Count
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_lazy
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
from django_filters.views import FilterView
from easy_pdf.views import PDFTemplateView

from dm_apps.utils import custom_send_mail
from lib.functions.custom_functions import fiscal_year, listrify
from shared_models import models as shared_models
from shared_models.views import CommonTemplateView, CommonFormsetView, CommonHardDeleteView, CommonFilterView, CommonDetailView, CommonListView, \
    CommonUpdateView
from . import emails
from . import filters
from . import forms
from . import models
from . import reports
from . import xml_export
from .mixins import SuperuserOrAdminRequiredMixin, CanModifyRequiredMixin, AdminRequiredMixin, InventoryBasicMixin, InventoryLoginRequiredMixin
from .utils import can_modify


# USER PERMISSIONS
class InventoryUserFormsetView(SuperuserOrAdminRequiredMixin, CommonFormsetView):
    template_name = 'inventory/formset.html'
    h1 = "Manage Data Inventory Users"
    queryset = models.InventoryUser.objects.all()
    formset_class = forms.InventoryUserFormset
    success_url_name = "inventory:manage_inventory_users"
    home_url_name = "inventory:index"
    delete_url_name = "inventory:delete_inventory_user"
    container_class = "container bg-light curvy"


class InventoryUserHardDeleteView(SuperuserOrAdminRequiredMixin, CommonHardDeleteView):
    model = models.InventoryUser
    success_url = reverse_lazy("inventory:manage_inventory_users")


# INDEX ETC

class Index(InventoryBasicMixin, CommonTemplateView):
    template_name = 'inventory/index.html'
    h1 = gettext_lazy("DFO Science Data Inventory")
    active_page_name_crumb = gettext_lazy("Home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        published_records = models.Resource.objects.filter(fgp_publication_date__isnull=False).count()
        context["published_records"] = published_records

        flagged_4_deletion = models.Resource.objects.filter(flagged_4_deletion=True).count()
        context["flagged_4_deletion"] = flagged_4_deletion

        flagged_4_publication = models.Resource.objects.filter(flagged_4_publication=True).count()
        context["flagged_4_publication"] = flagged_4_publication

        return context


class OpenDataDashboardTemplateView(InventoryBasicMixin, CommonTemplateView):
    template_name = 'inventory/open_data_dashboard.html'
    h1 = gettext_lazy("Open Data Dashboard")
    home_url_name = "inventory:index"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_fy = shared_models.FiscalYear.objects.get(pk=fiscal_year(sap_style=True))
        context["current_fy"] = current_fy
        my_dict = dict()
        qs = models.Resource.objects.all().order_by("-last_revision_date", "-fgp_publication_date")
        my_dict["TOTAL"] = dict()
        my_dict["TOTAL"]["qs_total"] = qs.count()
        my_dict["TOTAL"]["qs_fgp"] = qs.filter(fgp_publication_date__isnull=False).count()
        my_dict["TOTAL"]["qs_open_data"] = qs.filter(public_url__isnull=False).count()
        my_dict["TOTAL"]["qs_open_data_current_fy"] = qs.filter(fgp_publication_date__isnull=False,
                                                                publication_fy=current_fy, public_url__isnull=False).count()

        for region in shared_models.Region.objects.all():
            regional_qs = qs.filter(section__division__branch__region=region)
            my_dict[region] = dict()
            my_dict[region]["qs_total"] = regional_qs
            my_dict[region]["qs_fgp"] = regional_qs.filter(fgp_publication_date__isnull=False)
            my_dict[region]["qs_open_data"] = regional_qs.filter(public_url__isnull=False)
            my_dict[region]["qs_open_data_current_fy"] = regional_qs.filter(fgp_publication_date__isnull=False,
                                                                            publication_fy=current_fy,
                                                                            public_url__isnull=False)

        # unsorted
        regional_qs = qs.filter(section__isnull=True)
        my_dict["unsorted"] = dict()
        my_dict["unsorted"]["qs_total"] = regional_qs
        my_dict["unsorted"]["qs_fgp"] = regional_qs.filter(fgp_publication_date__isnull=False)
        my_dict["unsorted"]["qs_open_data"] = regional_qs.filter(public_url__isnull=False)
        my_dict["unsorted"]["qs_open_data_current_fy"] = regional_qs.filter(fgp_publication_date__isnull=False,
                                                                            publication_fy=current_fy,
                                                                            public_url__isnull=False)

        context["my_dict"] = my_dict
        context['field_list'] = [
            "t_title|Title",
            "section|DFO Section",
            "last_publication|Published to Open Data",
            "publication_fy|FY of latest publication",
            "external_links|External links",
        ]

        od_keywords = [kw.non_hierarchical_name_en for r in qs.filter(public_url__isnull=False, fgp_publication_date__isnull=False) for kw
                       in r.keywords.all()]
        od_keywords_set = set(od_keywords)
        frequency_list = list()
        for kw in od_keywords_set:
            frequency_list.append({
                "text": kw,
                "size": od_keywords.count(kw) * 10,
            })

        context["frequency_list"] = json.dumps(frequency_list)
        # context["words"] = listrify([kw for kw in od_keywords])

        return context


# RESOURCE #
############


class ResourceListView(InventoryBasicMixin, CommonFilterView):
    filterset_class = filters.ResourceFilter
    template_name = 'inventory/resource_list.html'
    queryset = models.Resource.objects.order_by("-status", "title_eng").annotate(
        search_term=Concat('title_eng', Value(" "),
                           'descr_eng', Value(" "),
                           'purpose_eng', Value(" "),
                           'uuid', Value(" "),
                           'odi_id',
                           output_field=TextField()))
    home_url_name = "inventory:index"
    container_class = "container-fluid"
    row_object_url_name = "inventory:resource_detail"
    new_object_url = "inventory:resource_new"
    paginate_by = 25
    field_list = [
        {"name": 'region', "class": "", "width": ""},
        {"name": 't_title|{}'.format(gettext_lazy("title")), "class": "w-30", "width": ""},
        {"name": 'resource_type', "class": "", "width": ""},
        {"name": 'status', "class": "", "width": ""},
        {"name": 'section', "class": "w-15", "width": ""},
        {"name": 'Previous time certified', "class": "", "width": ""},
        {"name": 'completeness rating', "class": "", "width": ""},
        {"name": 'translation_needed', "class": "", "width": ""},
    ]


class MyResourceListView(InventoryLoginRequiredMixin, CommonListView):
    model = models.Resource
    template_name = 'inventory/resource_list.html'
    home_url_name = "inventory:index"
    container_class = "container-fluid"
    row_object_url_name = "inventory:resource_detail"
    new_object_url = "inventory:resource_new"
    field_list = [
        {"name": 't_title|Title', "class": ""},
        {"name": 'status', "class": ""},
        {"name": 'date_last_modified', "class": ""},
        {"name": 'last_modified_by', "class": ""},
        {"name": 'roles|Role(s)', "class": ""},
        {"name": 'Previous time certified', "class": ""},
        {"name": 'Completeness rating', "class": ""},
        {"name": 'open_data|Published to Open Data', "class": ""},
    ]

    def get_queryset(self):
        qs = models.Resource.objects.filter(resource_people__person_id=self.request.user.id).distinct().order_by("-date_last_modified")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["personal"] = True
        return context


class ResourceDetailView(InventoryBasicMixin, CommonDetailView):
    model = models.Resource
    template_name = "inventory/resource_detail/resource_detail.html"

    def get_object(self, queryset=None):
        if self.kwargs.get("uuid"):
            return get_object_or_404(self.model, uuid=self.kwargs.get("uuid"))
        return super().get_object(queryset)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self.kwargs.get("uuid"):
            return HttpResponseRedirect(reverse("inventory:resource_detail_uuid", kwargs={"uuid": obj.uuid}))

        xml_export.verify(obj)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kcount_other'] = self.object.keywords.filter(
            ~Q(keyword_domain_id=8) & ~Q(keyword_domain_id=6) & ~Q(keyword_domain_id=7) & Q(is_taxonomic=False)).count()
        context['kcount_tc'] = self.object.keywords.filter(keyword_domain_id__exact=8).count()
        context['kcount_cst'] = self.object.keywords.filter(keyword_domain_id__exact=6).count()
        context['kcount_tax'] = self.object.keywords.filter(is_taxonomic__exact=True).count()
        context['kcount_loc'] = self.object.keywords.filter(keyword_domain_id__exact=7).count()
        context['custodian_count'] = self.object.resource_people.filter(role=1).count()

        if self.object.completedness_rating == 1:
            context['verified'] = True
        else:
            context['verified'] = False

        my_resource = self.get_object()
        context['can_modify'] = can_modify(self.request.user, my_resource.id)
        return context


class ResourceDetailPDFView(InventoryBasicMixin, PDFTemplateView):
    def get_pdf_filename(self):
        my_object = models.Resource.objects.get(pk=self.kwargs.get("pk"))
        return f"{my_object.uuid}.pdf"

    template_name = 'inventory/resource_detail_pdf.html'
    field_list = [
        'uuid',
        'resource_type',
        'section',
        'title_eng',
        'title_fre',
        'status',
        'maintenance',
        'purpose_eng',
        'purpose_fre',
        'descr_eng',
        'descr_fre',
        'time_period|time period',
        'security_classification',
        'storage_envr_notes',
        'distribution_formats',
        'data_char_set',
        'spat_representation',
        'spat_ref_system',
        'notes',
        # 'citations',
        # 'keywords',
        # 'people',
        # 'parent',
        # 'date_last_modified',
        # 'last_modified_by',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = models.Resource.objects.get(pk=self.kwargs.get("pk"))
        context["field_list"] = self.field_list
        context["now"] = timezone.now()
        return context


class ResourceUpdateView(CanModifyRequiredMixin, CommonUpdateView):
    model = models.Resource
    form_class = forms.ResourceForm
    home_url_name = "inventory:index"
    template_name = "inventory/resource_form.html"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("inventory:resource_detail", args=[self.get_object().id])}

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'date_last_modified': timezone.now(),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get lists
        resource_list = ['<a href="#id_parent" class="resource_insert" code="{id}" url="{url}">{text}</a>'.format(id=obj.id, text=str(obj),
                                                                                                                  url=reverse(
                                                                                                                      'inventory:resource_detail',
                                                                                                                      kwargs={
                                                                                                                          'pk': obj.id}))
                         for obj in models.Resource.objects.all()]
        context['resource_list'] = resource_list
        return context



class ResourceCloneUpdateView(ResourceUpdateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cloning"] = True
        return context

    def test_func(self):
        return self.request.user.is_authenticated

    def get_initial(self):
        init = super().get_initial()
        init["cloning"] = True
        init["title_eng"] = "CLONE OF: " + self.get_object().title_eng
        return init

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        old_obj = models.Resource.objects.get(pk=new_obj.pk)

        new_obj.pk = None
        new_obj.uuid = None
        new_obj.odi_id = None
        new_obj.public_url = None
        new_obj.fgp_url = None
        new_obj.od_publication_date = None
        new_obj.fgp_publication_date = None
        new_obj.od_release_date = None
        new_obj.last_revision_date = None
        new_obj.date_verified = None
        new_obj.save()

        """
    people = models.ManyToManyField(Person, through='ResourcePerson')
    
    
    
        """
        for item in old_obj.paa_items.all():
            new_obj.paa_items.add(item)

        for item in old_obj.keywords.all():
            new_obj.keywords.add(item)

        for item in old_obj.distribution_formats.all():
            new_obj.distribution_formats.add(item)

        for item in old_obj.citations2.all():
            new_obj.citations2.add(item)

        # Now we need to replicate all the related records:
        # 1) resource people
        for old_rel_obj in old_obj.resource_people.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.resource = new_obj
            new_rel_obj.save()

        # 2) data resources
        for old_rel_obj in old_obj.data_resources.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.resource = new_obj
            new_rel_obj.save()

        # 3) web services
        for old_rel_obj in old_obj.web_services.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.resource = new_obj
            new_rel_obj.save()

        return HttpResponseRedirect(reverse_lazy("inventory:resource_detail", args=[new_obj.id]))


class ResourceCreateView(InventoryLoginRequiredMixin, CreateView):
    model = models.Resource
    form_class = forms.ResourceCreateForm

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'date_last_modified': timezone.now(),
            'add_custodian': True,
            'add_point_of_contact': True,
        }

    def form_valid(self, form):
        my_object = form.save()
        if form.cleaned_data['add_custodian'] == True:
            models.ResourcePerson.objects.create(resource_id=my_object.id, person_id=self.request.user.id, role_id=1)

        # if form.cleaned_data['add_point_of_contact'] == True:
        #     models.ResourcePerson.objects.create(resource_id=object.id, person_id=50, role_id=4)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get lists
        resource_list = ['<a href="#" class="resource_insert" code={id}>{text}</a>'.format(id=obj.id, text=str(obj)) for obj in
                         models.Resource.objects.all()]
        context['resource_list'] = resource_list
        return context


class ResourceDeleteView(CanModifyRequiredMixin, DeleteView):
    model = models.Resource
    success_url = reverse_lazy('inventory:resource_list')
    success_message = 'The data resource was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class ResourceDeleteFlagUpdateView(InventoryLoginRequiredMixin, UpdateView):
    model = models.Resource

    template_name = "inventory/resource_flag_deletion.html"
    form_class = forms.ResourceFlagging

    def get_initial(self):
        if self.object.flagged_4_deletion:
            return {
                'flagged_4_deletion': False,
            }
        else:
            return {
                'flagged_4_deletion': True,
            }

    def form_valid(self, form):
        object = form.save()
        if object.flagged_4_deletion:
            email = emails.FlagForDeletionEmail(self.object, self.request.user, self.request)
            # send the email object
            custom_send_mail(
                subject=email.subject,
                html_message=email.message,
                from_email=email.from_email,
                recipient_list=email.to_list
            )

            messages.success(self.request,
                             'The data resource has been flagged for deletion and the regional data manager has been notified!')
        else:
            messages.success(self.request, 'The data resource has been unflagged!')
        return HttpResponseRedirect(reverse('inventory:resource_detail', kwargs={"pk": self.kwargs["pk"]}))


class ResourcePublicationFlagUpdateView(InventoryLoginRequiredMixin, UpdateView):
    model = models.Resource

    template_name = "inventory/resource_flag_publication.html"
    form_class = forms.ResourceFlagging

    def get_initial(self):
        if self.object.flagged_4_publication:
            return {
                'flagged_4_publication': False,
            }
        else:
            return {
                'flagged_4_publication': True,
            }

    def form_valid(self, form):
        object = form.save()
        if object.flagged_4_publication:
            email = emails.FlagForPublicationEmail(self.object, self.request.user, self.request)
            # send the email object
            custom_send_mail(
                subject=email.subject,
                html_message=email.message,
                from_email=email.from_email,
                recipient_list=email.to_list
            )
            messages.success(self.request,
                             'The data resource has been flagged for publication and the regional data manager has been notified!')
        else:
            messages.success(self.request, 'The data resource has been unflagged!')
        return HttpResponseRedirect(reverse('inventory:resource_detail', kwargs={"pk": self.kwargs["pk"]}))


# RESOURCE PERSON #
###################

class ResourcePersonFilterView(CanModifyRequiredMixin, FilterView):
    filterset_class = filters.PersonFilter
    template_name = "inventory/resource_person_filter.html"

    def get_queryset(self):
        return models.Person.objects.annotate(search_term=Concat(
            'user__first_name',
            Value(" "),
            'user__last_name',
            Value(" "),
            'user__email',
            output_field=TextField()
        ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.kwargs['resource']
        my_resource = models.Resource.objects.get(id=resource)
        context['resource'] = my_resource

        return context


class ResourcePersonCreateView(CanModifyRequiredMixin, CreateView):
    model = models.ResourcePerson
    template_name = 'inventory/resource_person_form.html'
    form_class = forms.ResourcePersonForm

    def get_initial(self):
        resource = models.Resource.objects.get(pk=self.kwargs['resource'])
        person = models.Person.objects.get(user_id=self.kwargs['person'])
        return {
            'resource': resource,
            'person': person,
            # 'last_modified_by': self.request.user,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = models.Resource.objects.get(id=self.kwargs['resource'])
        context['resource'] = resource
        person = models.Person.objects.get(user_id=self.kwargs['person'])
        context['person'] = person
        return context

    def form_valid(self, form):
        object = form.save()

        # if the person is being added as a custodian
        if object.role.id == 1:
            email = emails.AddedAsCustodianEmail(object.resource, object.person.user, self.request)
            # send the email object
            custom_send_mail(
                subject=email.subject,
                html_message=email.message,
                from_email=email.from_email,
                recipient_list=email.to_list
            )
            messages.success(self.request,
                             '{} has been added as {} and a notification email has been sent to them!'.format(
                                 object.person.full_name, object.role))
        else:
            messages.success(self.request, '{} has been added as {}!'.format(object.person.full_name, object.role))

        return super().form_valid(form)


class ResourcePersonUpdateView(CanModifyRequiredMixin, UpdateView):
    model = models.ResourcePerson
    template_name = 'inventory/resource_person_form.html'
    form_class = forms.ResourcePersonForm

    def form_valid(self, form):
        object = form.save()

        # if the person is being added as a custodian
        if object.role.id == 1:
            email = emails.AddedAsCustodianEmail(object.resource, object.person.user, self.request)
            # send the email object
            custom_send_mail(
                subject=email.subject,
                html_message=email.message,
                from_email=email.from_email,
                recipient_list=email.to_list
            )
            messages.success(self.request,
                             '{} has been added as {} and a notification email has been sent to them!'.format(
                                 object.person.full_name, object.role))
        else:
            messages.success(self.request, '{} has been added as {}!'.format(object.person.full_name, object.role))

        return super().form_valid(form)


class ResourcePersonDeleteView(CanModifyRequiredMixin, DeleteView):
    model = models.ResourcePerson
    template_name = 'inventory/resource_person_confirm_delete.html'
    success_url = reverse_lazy('inventory:resource_person')
    success_message = 'The person has been removed from the data resource!'

    def delete(self, request, *args, **kwargs):
        object = models.ResourcePerson.objects.get(pk=self.kwargs["pk"])

        # if the person is being added as a custodian
        if object.role.id == 1:

            email = emails.RemovedAsCustodianEmail(object.resource, object.person.user, self.request)
            # send the email object
            custom_send_mail(
                subject=email.subject,
                html_message=email.message,
                from_email=email.from_email,
                recipient_list=email.to_list
            )
            messages.success(self.request,
                             '{} has been removed as {} and a notification email has been sent to them!'.format(
                                 object.person.full_name, object.role))
        else:
            messages.success(self.request, '{} has been removed as {}!'.format(object.person.full_name, object.role))

        # messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('inventory:resource_detail', kwargs={'pk': self.object.resource.id})


# PERSON #
##########

# this is a complicated cookie. Therefore we will not use a model view or model form and handle the clean data manually.
class PersonCreateView(InventoryLoginRequiredMixin, FormView):
    template_name = 'inventory/person_form.html'
    form_class = forms.PersonCreateForm

    def get_initial(self):
        return {
            "organization": 6,
        }

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        # form.send_email() cool to know you can call methods off of the form like this...

        # step 0: retrieve data from form
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        position_eng = form.cleaned_data['position_eng']
        position_fre = form.cleaned_data['position_fre']
        phone = form.cleaned_data['phone']
        language = form.cleaned_data['language']
        organization = form.cleaned_data['organization']

        # # step 1: create a new user - since we added the receiver decorator to models.py, we do not have to create a person. It will be handled automatically.
        user = User.objects.create(
            username=email,
            first_name=first_name,
            last_name=last_name,
            password="pbkdf2_sha256$120000$ctoBiOUIJMD1$DWVtEKBlDXXHKfy/0wKCpcIDYjRrKfV/wpYMHKVrasw=",
            is_active=1,
            email=email,
        )

        # step 2: fetch the Person
        new_person = models.Person.objects.get(user_id=user.id)
        new_person.position_eng = position_eng
        new_person.position_fre = position_fre
        new_person.phone = phone

        if language != "":
            new_person.language = int(language)

        if organization != "":
            new_person.organization_id = organization.id

        new_person.save()

        # finally go to the create new resource person page
        return HttpResponseRedirect(reverse_lazy('inventory:resource_person_add', kwargs={
            'resource': self.kwargs['resource'],
            'person': new_person.user.id,
        }))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = models.Resource.objects.get(id=self.kwargs['resource'])
        context['resource'] = resource
        return context


class PersonCreateViewPopout(InventoryLoginRequiredMixin, FormView):
    template_name = 'inventory/person_form_popout.html'
    form_class = forms.PersonCreateForm

    def get_initial(self):
        return {
            "organization": 6,
        }

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        # form.send_email() cool to know you can call methods off of the form like this...

        # step 0: retrieve data from form
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        position_eng = form.cleaned_data['position_eng']
        position_fre = form.cleaned_data['position_fre']
        phone = form.cleaned_data['phone']
        language = form.cleaned_data['language']
        organization = form.cleaned_data['organization']

        # # step 1: create a new user - since we added the receiver decorator to models.py, we do not have to create a person. It will be handled automatically.
        user = User.objects.create(
            username=email,
            first_name=first_name,
            last_name=last_name,
            password="pbkdf2_sha256$120000$ctoBiOUIJMD1$DWVtEKBlDXXHKfy/0wKCpcIDYjRrKfV/wpYMHKVrasw=",
            is_active=1,
            email=email,
        )

        # step 2: fetch the Person
        new_person = models.Person.objects.get(user_id=user.id)
        new_person.position_eng = position_eng
        new_person.position_fre = position_fre
        new_person.phone = phone

        if language != "":
            new_person.language = int(language)

        if organization != "":
            new_person.organization = organization

        new_person.save()

        # finally close the form
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PersonUpdateView(InventoryLoginRequiredMixin, FormView):
    template_name = 'inventory/person_form.html'
    form_class = forms.PersonForm

    def get_success_url(self):
        try:
            self.kwargs['resource']
        except KeyError:
            print("no resource id")
            return reverse_lazy('inventory:my_resource_list')
        else:
            return reverse_lazy('inventory:resource_detail', kwargs={
                'pk': self.kwargs['resource'],
            })

    def get_initial(self):
        person = models.Person.objects.get(pk=self.kwargs['person'])
        return {
            'first_name': person.user.first_name,
            'last_name': person.user.last_name,
            'email': person.user.email,
            'position_eng': person.position_eng,
            'position_fre': person.position_fre,
            'phone': person.phone,
            'language': person.language,
            'organization': person.organization_id,
        }

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        old_person = models.Person.objects.get(pk=self.kwargs['person'])

        # step 0: retreive data from form
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        position_eng = form.cleaned_data['position_eng']
        position_fre = form.cleaned_data['position_fre']
        phone = form.cleaned_data['phone']
        language = form.cleaned_data['language']
        organization = form.cleaned_data['organization']

        # step 2: Retrieve the Person model
        old_person.user.first_name = first_name
        old_person.user.last_name = last_name
        old_person.user.email = email
        old_person.user.username = email

        old_person.position_eng = position_eng
        old_person.position_fre = position_fre
        old_person.phone = phone

        if language == "" or language is None:
            old_person.language = None
        else:
            old_person.language = int(language)

        if organization == "" or organization is None:
            old_person.organization_id = None
        else:
            old_person.organization = organization

        old_person.user.save()
        old_person.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            resource = models.Resource.objects.get(id=self.kwargs['resource'])
            context['resource'] = resource
        except KeyError:
            print("no resource id")

        person = models.Person.objects.get(user_id=self.kwargs['person'])
        context['person'] = person
        return context


# RESOURCE KEYWORD #
####################


class ResourceKeywordUpdateView(CanModifyRequiredMixin, UpdateView):
    model = models.Resource
    template_name = "inventory/resource_keyword_form.html"
    form_class = forms.ResourceKeywordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["top_20_tc"] = models.Keyword.objects.filter(keyword_domain=8).annotate(resource_count=Count("resources")).order_by(
            "-resource_count")[:10]
        context["top_20_cs"] = models.Keyword.objects.filter(keyword_domain=6).annotate(resource_count=Count("resources")).order_by(
            "-resource_count")[:10]
        context["top_20_tax"] = models.Keyword.objects.filter(is_taxonomic=True).annotate(resource_count=Count("resources")).order_by(
            "-resource_count")[:10]
        context["top_20_area"] = models.Keyword.objects.filter(keyword_domain=7).annotate(resource_count=Count("resources")).order_by(
            "-resource_count")[:10]
        context["top_20_gen"] = models.Keyword.objects.filter(
            ~Q(keyword_domain_id=8) & ~Q(keyword_domain_id=6) & ~Q(keyword_domain_id=7) & Q(is_taxonomic=False)
        ).annotate(resource_count=Count("resources")).order_by("-resource_count")[:10]
        return context


class ResourceKeywordFilterView(CanModifyRequiredMixin, FilterView):
    filterset_class = filters.KeywordFilter
    template_name = "inventory/resource_keyword_filter.html"
    queryset = models.Keyword.objects.annotate(
        search_term=Concat('text_value_eng', Value(' '), 'details', output_field=TextField())).filter(
        ~Q(keyword_domain_id=8) & ~Q(keyword_domain_id=6) & ~Q(keyword_domain_id=7) & Q(is_taxonomic=False)).order_by(
        'text_value_eng')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.kwargs['resource']
        my_resource = models.Resource.objects.get(id=resource)
        context['resource'] = my_resource
        context['keyword_type'] = "Keyword"
        return context


class ResourceTopicCategoryFilterView(InventoryBasicMixin, FilterView):
    filterset_class = filters.KeywordFilter
    template_name = "inventory/resource_keyword_filter.html"
    queryset = models.Keyword.objects.annotate(
        search_term=Concat('text_value_eng', Value(' '), 'details', output_field=TextField())).filter(
        keyword_domain_id__exact=8).order_by('text_value_eng')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.kwargs['resource']
        my_resource = models.Resource.objects.get(id=resource)
        context['resource'] = my_resource
        context['keyword_type'] = "Topic Category"
        return context


class ResourceCoreSubjectFilterView(InventoryBasicMixin, FilterView):
    filterset_class = filters.KeywordFilter
    template_name = "inventory/resource_keyword_filter.html"
    queryset = models.Keyword.objects.annotate(
        search_term=Concat('text_value_eng', Value(' '), 'details', output_field=TextField())).filter(
        keyword_domain_id__exact=6).order_by('text_value_eng')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.kwargs['resource']
        my_resource = models.Resource.objects.get(id=resource)
        context['resource'] = my_resource
        context['keyword_type'] = "Core Subject"
        return context


class ResourceSpeciesFilterView(InventoryBasicMixin, FilterView):
    filterset_class = filters.KeywordFilter
    template_name = "inventory/resource_keyword_filter.html"
    queryset = models.Keyword.objects.annotate(
        search_term=Concat('text_value_eng', Value(' '), 'details', Value(' '), 'uid', output_field=TextField())).filter(
        is_taxonomic=True).order_by('text_value_eng')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.kwargs['resource']
        my_resource = models.Resource.objects.get(id=resource)
        context['resource'] = my_resource
        context['keyword_type'] = "Taxonomic Keyword"
        return context


class ResourceLocationFilterView(InventoryBasicMixin, FilterView):
    filterset_class = filters.KeywordFilter
    template_name = "inventory/resource_keyword_filter.html"
    queryset = models.Keyword.objects.annotate(
        search_term=Concat('text_value_eng', Value(' '), 'details', output_field=TextField())).filter(
        keyword_domain_id__exact=7).order_by('text_value_eng')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.kwargs['resource']
        my_resource = models.Resource.objects.get(id=resource)
        context['resource'] = my_resource
        context['keyword_type'] = "DFO Area"
        return context


def resource_keyword_add(request, resource, keyword, keyword_type=None):
    my_keyword = models.Keyword.objects.get(pk=keyword)
    my_resource = models.Resource.objects.get(pk=resource)

    if my_resource.keywords.filter(pk=keyword).count() > 0:
        messages.warning(request, "'{}' has already been added as a keyword.".format(my_keyword.text_value_eng))
    else:
        my_resource.keywords.add(keyword)
        messages.success(request, "'{}' has been added as a keyword.".format(my_keyword.text_value_eng))

    if keyword_type == "topic-category":
        return HttpResponseRedirect(reverse('inventory:resource_topic_category_filter', kwargs={'resource': resource}))
    elif keyword_type == "core-subject":
        return HttpResponseRedirect(reverse('inventory:resource_core_subject_filter', kwargs={'resource': resource}))
    elif keyword_type == "taxonomic-keyword":
        return HttpResponseRedirect(reverse('inventory:resource_species_filter', kwargs={'resource': resource}))
    elif keyword_type == "keyword":
        return HttpResponseRedirect(reverse('inventory:resource_keyword_filter', kwargs={'resource': resource}))
    elif keyword_type == "dfo-area":
        return HttpResponseRedirect(reverse('inventory:resource_location_filter', kwargs={'resource': resource}))
    else:
        return HttpResponseRedirect(reverse('inventory:resource_keyword_edit', kwargs={'pk': resource}))


def resource_keyword_delete(request, resource, keyword):
    my_keyword = models.Keyword.objects.get(pk=keyword)
    my_resource = models.Resource.objects.get(pk=resource)

    my_resource.keywords.remove(keyword)
    messages.success(request, "'{}' has been removed.".format(my_keyword.text_value_eng))

    return HttpResponseRedirect(reverse('inventory:resource_detail', kwargs={'pk': resource}))


# KEYWORD #
###########

class KeywordDetailView(InventoryBasicMixin, DetailView):
    model = models.Keyword

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_resource = models.Resource.objects.get(id=self.kwargs['resource'])
        context['resource'] = my_resource
        return context


class KeywordUpdateView(InventoryLoginRequiredMixin, UpdateView):
    model = models.Keyword
    form_class = forms.KeywordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_resource = models.Resource.objects.get(id=self.kwargs['resource'])
        context['resource'] = my_resource
        return context

    def get_success_url(self):
        return reverse_lazy('inventory:keyword_detail', kwargs={
            'resource': self.kwargs['resource'],
            'pk': self.kwargs['pk'],
        })


class KeywordCreateView(InventoryLoginRequiredMixin, CreateView):
    model = models.Keyword
    form_class = forms.KeywordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_resource = models.Resource.objects.get(id=self.kwargs['resource'])
        context['resource'] = my_resource
        return context

    def form_valid(self, form):
        self.object = form.save()
        my_resource = models.Resource.objects.get(pk=self.kwargs['resource']).keywords.add(self.object.id)
        messages.success(self.request, "'{}' has been added as a keyword.".format(self.object.text_value_eng))
        return HttpResponseRedirect(reverse('inventory:resource_detail', kwargs={'pk': self.kwargs['resource']}))


def keyword_delete(request, resource, keyword):
    my_keyword = models.Keyword.objects.get(pk=keyword)
    my_keyword.delete()
    messages.success(request, "'{}' has been removed from the database.".format(my_keyword.text_value_eng))
    return HttpResponseRedirect(reverse('inventory:resource_detail', kwargs={'pk': resource}))


# RESOURCE CITATION #
####################

class ResourceCitationFilterView(CanModifyRequiredMixin, CommonFilterView):
    filterset_class = filters.CitationFilter
    template_name = "inventory/resource_citation_filter.html"
    queryset = shared_models.Citation.objects.annotate(
        search_term=Concat('name', Value(' '), 'nom', Value(' '), 'pub_number', Value(' '), 'year',
                           Value(' '), 'series', output_field=TextField())).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.kwargs['resource']
        my_resource = models.Resource.objects.get(id=resource)
        context['resource'] = my_resource
        return context


def resource_citation_add(request, resource, citation):
    my_citation = shared_models.Citation.objects.get(pk=citation)
    my_resource = models.Resource.objects.get(pk=resource)

    if my_resource.citations2.filter(pk=citation).count() > 0:
        messages.warning(request, "'{}' has already been added as a citation.".format(my_citation.title))
    else:
        my_resource.citations2.add(citation)
        messages.success(request, "'{}' has been added as a citation.".format(my_citation.title))

    return HttpResponseRedirect(reverse('inventory:resource_citation_filter', kwargs={'resource': resource}))


def resource_citation_delete(request, resource, citation):
    my_citation = shared_models.Citation.objects.get(pk=citation)
    my_resource = models.Resource.objects.get(pk=resource)

    my_resource.citations2.remove(citation)
    messages.success(request, "'{}' has been removed.".format(my_citation.title))

    return HttpResponseRedirect(reverse('inventory:resource_detail', kwargs={'pk': resource}))


# CITATION #
############

class CitationDetailView(InventoryBasicMixin, DetailView):
    model = shared_models.Citation
    template_name = 'inventory/citation_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_resource = models.Resource.objects.get(id=self.kwargs['resource'])
        context['resource'] = my_resource
        return context


class CitationUpdateView(InventoryLoginRequiredMixin, UpdateView):
    model = shared_models.Citation
    form_class = forms.CitationForm
    template_name = 'inventory/citation_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_resource = models.Resource.objects.get(id=self.kwargs['resource'])
        context['resource'] = my_resource
        return context

    def get_success_url(self):
        return reverse_lazy('inventory:citation_detail', kwargs={
            'resource': self.kwargs['resource'],
            'pk': self.kwargs['pk'],
        })


class CitationCreateView(InventoryLoginRequiredMixin, CreateView):
    model = shared_models.Citation
    form_class = forms.CitationForm
    template_name = 'inventory/citation_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_resource = models.Resource.objects.get(id=self.kwargs['resource'])
        context['resource'] = my_resource
        return context

    def form_valid(self, form):
        self.object = form.save()
        my_resource = models.Resource.objects.get(pk=self.kwargs['resource']).citations2.add(self.object.id)
        messages.success(self.request, "'{}' has been added as a citation.".format(self.object.title))
        return HttpResponseRedirect(reverse('inventory:resource_detail', kwargs={'pk': self.kwargs['resource']}))


@login_required(login_url='/accounts/login/')
def citation_delete(request, resource, citation):
    my_citation = shared_models.Citation.objects.get(pk=citation)
    my_citation.delete()
    messages.success(request, "'{}' has been removed from the database.".format(my_citation.title))
    return HttpResponseRedirect(reverse('inventory:resource_detail', kwargs={'pk': resource}))


# PUBLICATION #
###############

class PublicationCreateView(InventoryLoginRequiredMixin, CreateView):
    model = shared_models.Publication
    fields = "__all__"

    template_name = 'inventory/publication_form_popout.html'

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(reverse('shared_models:close_me'))


# XML GOODNESS #
################

def export_resource_xml(request, resource, publish):
    # grab resource instance
    my_resource = models.Resource.objects.get(pk=resource)

    if publish == "yes":
        # if there is already a publication date, let's not overwrite it.
        if my_resource.fgp_publication_date:
            my_resource.last_revision_date = timezone.now()
        else:
            my_resource.fgp_publication_date = timezone.now()
        my_resource.flagged_4_publication = False

        my_resource.save()

    # Create the HttpResponse object
    filename = "xml_metadata_export_{}.xml".format(my_resource.id)
    response = HttpResponse(content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

    # pass the object to the xml builder module
    xml_data = xml_export.construct(my_resource)

    response.write(xml_data)
    # print(xml_data)
    return response
    # return HttpResponseRedirect(reverse('inventory:resource_detail', kwargs={'pk':resource}))


# DATA MANAGEMENT ADMIN #
#########################

class DataManagementCustodianListView(AdminRequiredMixin, TemplateView):
    template_name = 'inventory/dm_custodian_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = models.ResourcePerson.objects.filter(role=1).order_by("person__user__last_name",
                                                                         "person__user__first_name")

        # retain only the unique items, and keep them in order according to keys (cannot use a set for this reason)
        custodian_dict = OrderedDict()
        for item in queryset:
            custodian_dict[item.person.user_id] = item

        # convert the dict back into a list
        custodian_list = []
        for item in custodian_dict:
            custodian_list.append(custodian_dict[item])

        context['custodian_list'] = custodian_list
        context['custodian_count'] = len(custodian_list)

        context['now'] = timezone.now()

        return context


class DataManagementCustodianDetailView(AdminRequiredMixin, DetailView):
    template_name = 'inventory/dm_custodian_detail.html'
    model = models.Person

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.object.resource_people.filter(role=1)
        me = models.Person.objects.get(user=User.objects.get(pk=self.request.user.id))
        email = emails.CertificationRequestEmail(me, self.object, self.request)
        context['queryset'] = queryset
        context['email'] = email
        context['now'] = timezone.now()
        # context['custodian_count'] = len(custodian_list)
        return context


def send_certification_request(request, person):
    # grab a copy of the resource
    my_person = models.Person.objects.get(pk=person)
    # create a new email object
    me = models.Person.objects.get(user=User.objects.get(pk=request.user.id))
    email = emails.CertificationRequestEmail(me, my_person, request)
    # send the email object
    custom_send_mail(
        subject=email.subject,
        html_message=email.message,
        from_email=email.from_email,
        recipient_list=email.to_list
    )
    my_person.user.correspondences.create(subject="Request for certification")
    messages.success(request, "the email has been sent and the correspondence has been logged!")
    return HttpResponseRedirect(reverse('inventory:dm_custodian_detail', kwargs={'pk': my_person.user_id}))


class PublishedResourcesListView(AdminRequiredMixin, ListView):
    template_name = "inventory/dm_published_resource.html"
    queryset = models.Resource.objects.filter(fgp_publication_date__isnull=False)


class FlaggedListView(AdminRequiredMixin, ListView):
    template_name = "inventory/dm_flagged_list.html"

    def get_queryset(self):
        if self.kwargs["flag_type"] == "publication":
            queryset = models.Resource.objects.filter(flagged_4_publication=True)
        elif self.kwargs["flag_type"] == "deletion":
            queryset = models.Resource.objects.filter(flagged_4_deletion=True)
        return queryset


class CertificationListView(AdminRequiredMixin, ListView):
    template_name = "inventory/dm_certification_list.html"
    queryset = models.ResourceCertification.objects.all().order_by("-certification_date")[:50]


class ModificationListView(AdminRequiredMixin, ListView):
    template_name = "inventory/dm_modification_list.html"
    queryset = models.Resource.objects.all().order_by("-date_last_modified")[:50]


class CustodianPersonUpdateView(AdminRequiredMixin, FormView):
    template_name = 'inventory/dm_custodian_form.html'
    form_class = forms.PersonCreateForm

    def get_success_url(self):
        return reverse_lazy('inventory:dm_custodian_detail', kwargs={
            'pk': self.kwargs['person'],
        })

    def get_initial(self):
        person = models.Person.objects.get(pk=self.kwargs['person'])
        return {
            'first_name': person.user.first_name,
            'last_name': person.user.last_name,
            'email': person.user.email,
            'position_eng': person.position_eng,
            'position_fre': person.position_fre,
            'phone': person.phone,
            'language': person.language,
            'organization': person.organization.id,
        }

    def form_valid(self, form):
        old_person = models.Person.objects.get(pk=self.kwargs['person'])

        # step 0: retreive data from form
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        position_eng = form.cleaned_data['position_eng']
        position_fre = form.cleaned_data['position_fre']
        phone = form.cleaned_data['phone']
        language = form.cleaned_data['language']
        organization = form.cleaned_data['organization']

        # step 2: Retrieve the Person model
        old_person.user.first_name = first_name
        old_person.user.last_name = last_name
        old_person.user.email = email
        old_person.user.username = email

        old_person.position_eng = position_eng
        old_person.position_fre = position_fre
        old_person.phone = phone

        if language != "":
            old_person.language = int(language)

        if organization != "":
            old_person.organization_id = int(organization)

        old_person.user.save()
        old_person.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = models.Person.objects.get(user_id=self.kwargs['person'])
        context['person'] = person
        return context


# RESOURCE CERTIFICATION #
##########################


class ResourceCertificationCreateView(CanModifyRequiredMixin, CreateView):
    model = models.ResourceCertification
    template_name = 'inventory/resource_certification_form.html'
    form_class = forms.ResourceCertificationForm
    success_message = "Certification successful!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_resource = models.Resource.objects.get(pk=self.kwargs['pk'])

        context['resource'] = my_resource
        return context

    def get_initial(self):
        return {
            'certifying_user': self.request.user,
            'resource': self.kwargs['pk'],
            'certification_date': timezone.now(),
        }

    def get_success_url(self):
        return reverse('inventory:resource_detail', kwargs={
            'pk': self.kwargs['pk'],
        })

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class ResourceCertificationDeleteView(CanModifyRequiredMixin, DeleteView):
    model = models.ResourceCertification
    template_name = 'inventory/resource_certification_confirm_delete.html'
    success_message = "The certification event has been removed."

    def get_success_url(self):
        return reverse('inventory:resource_detail', kwargs={
            'pk': self.object.resource.id,
        })

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# FILES #
#########

class FileCreateView(CanModifyRequiredMixin, CreateView):
    template_name = "inventory/file_form.html"
    model = models.File
    form_class = forms.FileForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy("inventory:resource_detail", kwargs={"pk": object.resource.id}))

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        context["editable"] = True
        resource = models.Resource.objects.get(pk=self.kwargs['resource'])
        context["resource"] = resource
        return context

    def get_initial(self):
        resource = models.Resource.objects.get(pk=self.kwargs['resource'])
        return {'resource': resource}


class FileDetailView(InventoryLoginRequiredMixin, UpdateView):
    template_name = "inventory/file_form.html"
    model = models.File
    form_class = forms.FileForm

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        context["editable"] = False
        return context


class FileUpdateView(CanModifyRequiredMixin, UpdateView):
    template_name = "inventory/file_form.html"
    model = models.File
    form_class = forms.FileForm

    def get_success_url(self, **kwargs):
        return reverse_lazy("inventory:resource_detail", kwargs={"pk": self.object.resource.id})

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        context["editable"] = True
        return context


class FileDeleteView(CanModifyRequiredMixin, DeleteView):
    template_name = "inventory/file_confirm_delete.html"
    model = models.File

    def get_success_url(self, **kwargs):
        return reverse_lazy("inventory:resource_detail", kwargs={"pk": self.object.resource.id})


# DATA RESOURCE #
#################

class DataResourceCreateView(CanModifyRequiredMixin, CreateView):
    template_name = "inventory/data_resource_form.html"
    model = models.DataResource
    form_class = forms.DataResourceForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy("inventory:resource_detail", kwargs={"pk": object.resource.id}))

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        resource = models.Resource.objects.get(pk=self.kwargs['resource'])
        context["resource"] = resource
        return context

    def get_initial(self):
        resource = models.Resource.objects.get(pk=self.kwargs['resource'])
        return {'resource': resource}


class DataResourceUpdateView(CanModifyRequiredMixin, UpdateView):
    template_name = "inventory/data_resource_form.html"
    model = models.DataResource
    form_class = forms.DataResourceForm

    def get_success_url(self, **kwargs):
        return reverse_lazy("inventory:resource_detail", kwargs={"pk": self.object.resource.id})

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        return context


class DataResourceDeleteView(CanModifyRequiredMixin, DeleteView):
    template_name = "inventory/data_resource_confirm_delete.html"
    model = models.DataResource

    def get_success_url(self, **kwargs):
        return reverse_lazy("inventory:resource_detail", kwargs={"pk": self.object.resource.id})


@login_required(login_url='/accounts/login/')
def data_resource_clone(request, pk):
    my_object = models.DataResource.objects.get(pk=pk)
    if can_modify(request.user, my_object.resource.id):
        my_object.id = None
        my_object.save()
    else:
        messages.error(request, _("Sorry, you do not have permissions to do this."))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# WEB SERVICES #
################

class WebServiceCreateView(CanModifyRequiredMixin, CreateView):
    template_name = "inventory/data_resource_form.html"
    model = models.WebService
    form_class = forms.WebServiceForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy("inventory:resource_detail", kwargs={"pk": object.resource.id}))

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        resource = models.Resource.objects.get(pk=self.kwargs['resource'])
        context["resource"] = resource
        return context

    def get_initial(self):
        resource = models.Resource.objects.get(pk=self.kwargs['resource'])
        return {'resource': resource}


class WebServiceUpdateView(CanModifyRequiredMixin, UpdateView):
    template_name = "inventory/data_resource_form.html"
    model = models.WebService
    form_class = forms.WebServiceForm

    def get_success_url(self, **kwargs):
        return reverse_lazy("inventory:resource_detail", kwargs={"pk": self.object.resource.id})

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        return context


class WebServiceDeleteView(CanModifyRequiredMixin, DeleteView):
    template_name = "inventory/data_resource_confirm_delete.html"
    model = models.WebService

    def get_success_url(self, **kwargs):
        return reverse_lazy("inventory:resource_detail", kwargs={"pk": self.object.resource.id})


@login_required(login_url='/accounts/login/')
def web_service_clone(request, pk):
    my_object = models.WebService.objects.get(pk=pk)
    if can_modify(request.user, my_object.resource.id):
        my_object.id = None
        my_object.save()
    else:
        messages.error(request, _("Sorry, you do not have permissions to do this."))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# REPORTS #
###########

class ReportSearchFormView(AdminRequiredMixin, FormView):
    template_name = 'inventory/report_search.html'
    form_class = forms.ReportSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        report = int(form.cleaned_data["report"])
        sections = listrify(form.cleaned_data["sections"], ",")
        regions = listrify(form.cleaned_data["regions"], ",")

        if sections == "":
            sections = "None"
        if regions == "":
            regions = "None"

        if report == 1:
            return HttpResponseRedirect(reverse("inventory:export_batch_xml", kwargs={
                'sections': sections,
            }))
        if report == 2:
            return HttpResponseRedirect(reverse("inventory:export_odi_report"))
        if report == 3:
            return HttpResponseRedirect(reverse("inventory:export_phyiscal_samples"))
        if report == 4:
            return HttpResponseRedirect(reverse("inventory:export_resources") + f"?sections={sections}")
        if report == 5:
            return HttpResponseRedirect(reverse("inventory:export_open_data_resources") + f"?regions={regions}")
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("inventory:report_search"))


def export_batch_xml(request, sections):
    file_url = reports.generate_batch_xml(sections)
    print(file_url)
    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/zip")
            response['Content-Disposition'] = 'inline; filename="xml_batch_export_{}.zip"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404

    # return HttpResponseRedirect(reverse("inventory:report_search"))


@login_required()
def export_odi_report(request):
    # print(trip)
    file_url = reports.generate_odi_report()
    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="ODI Report {}.xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


@login_required()
def export_phyiscal_samples(request):
    # print(trip)
    file_url = reports.generate_physical_samples_report()
    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="physical_samples_report {}.xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


@login_required()
def export_resources(request):
    sections = request.GET.get("sections") if request.GET.get("sections") else None
    file_url = reports.generate_resources_report(sections)
    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="resources report {}.xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


@login_required()
def export_open_data_resources(request):
    regions = request.GET.get("regions") if request.GET.get("regions") else None
    file_url = reports.generate_open_data_resources_report(regions)
    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="open data resources {}.xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404

#
# # TEMP #
# ########
#
#
# # this is a temp view DJF created to walkover the `program` field to the new `programs` field
# @login_required(login_url='/accounts/login/')
# @user_passes_test(in_inventory_dm_group, login_url='/accounts/denied/')
# def temp_formset(request, section):
#     context = {}
#     # if the formset is being submitted
#     if request.method == 'POST':
#         # choose the appropriate formset based on the `extra` arg
#         formset = forms.TempFormSet(request.POST)
#
#         if formset.is_valid():
#             formset.save()
#             # pass the specimen through the make_flags helper function to assign any QC flags
#
#             # redirect back to the observation_formset with the blind intention of getting another observation
#             return HttpResponseRedirect(reverse("inventory:formset"))
#     # otherwise the formset is just being displayed
#     else:
#         # prep the formset...for display
#         formset = forms.TempFormSet(
#             queryset=models.Resource.objects.filter(section_id=section).order_by("section")
#         )
#     context['formset'] = formset
#     context['my_object'] = models.Resource.objects.first()
#     context['field_list'] = ["title_eng", "section", "status", "descr_eng", "purpose_eng"]
#     return render(request, 'inventory/temp_formset.html', context)
