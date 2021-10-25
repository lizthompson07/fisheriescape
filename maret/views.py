from shared_models.views import CommonTemplateView, CommonFilterView, CommonCreateView, CommonFormsetView, \
    CommonDetailView, CommonDeleteView, CommonUpdateView, CommonPopoutUpdateView, CommonPopoutCreateView, \
    CommonPopoutDeleteView

from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils.translation import gettext as _, gettext_lazy
from django.utils.safestring import mark_safe
from django.db.models import TextField, Value
from django.db.models.functions import Concat

from django.urls import reverse_lazy, reverse

from maret.utils import UserRequiredMixin, AuthorRequiredMixin, AdminRequiredMixin
from maret import models, filters, forms

from masterlist import models as ml_models


class IndexView(UserRequiredMixin, CommonTemplateView):
    h1 = "home"
    template_name = 'maret/index.html'

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, mark_safe(_("Please note that only <b>unclassified information</b> may be entered into this application.")))
        return super().dispatch(request, *args, **kwargs)


#######################################################
# Person
#######################################################
class PersonListView(UserRequiredMixin, CommonFilterView):
    template_name = 'maret/maret_list.html'
    filterset_class = filters.PersonFilter
    model = ml_models.Person
    queryset = ml_models.Person.objects.annotate(
        search_term=Concat('first_name', 'last_name', 'designation', output_field=TextField()))
    field_list = [
        {"name": 'full_name_with_title|{}'.format(_("full name")), "class": "", "width": ""},
        {"name": 'phone_1', "class": "", "width": ""},
        # {"name": 'phone_2', "class": "", "width": ""},
        {"name": 'email_1', "class": "", "width": ""},
        {"name": 'last_updated|{}'.format(_("last updated")), "class": "", "width": ""},
    ]
    new_object_url_name = "maret:person_new"
    row_object_url_name = "maret:person_detail"
    home_url_name = "maret:index"
    paginate_by = 100
    h1 = _("Contacts")
    container_class = "container-fluid"


class PersonDetailView(UserRequiredMixin, CommonDetailView):
    model = ml_models.Person
    template_name = 'maret/person_detail.html'
    field_list = [
        "designation",
        "first_name",
        "last_name",
        "phone_1",
        "phone_2",
        "email_1",
        "email_2",
        "cell",
        "fax",
        "language",
        "notes",
        "metadata|{}".format(gettext_lazy("metadata")),
    ]
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Contacts"), "url": reverse_lazy("maret:person_list")}


class PersonCreateView(AuthorRequiredMixin, CommonCreateView):
    model = ml_models.Person
    form_class = forms.PersonForm
    parent_crumb = {"title": gettext_lazy("Person"), "url": reverse_lazy("maret:person_list")}
    template_name = "maret/form.html"
    h1 = gettext_lazy("New Contact")

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'created_by': self.request.user
        }


class PersonUpdateView(AuthorRequiredMixin, CommonUpdateView):
    model = ml_models.Person
    form_class = forms.PersonForm
    parent_crumb = {"title": gettext_lazy("Person"), "url": reverse_lazy("maret:person_list")}
    template_name = "maret/form.html"
    h1 = gettext_lazy("Contact")

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }

    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:person_detail", args=[obj.pk, ]))

        obj.save()
        return super().form_valid(form)


class PersonCreateViewPopout(AuthorRequiredMixin, CommonPopoutCreateView):
    model = ml_models.Person
    form_class = forms.PersonForm
    h1 = gettext_lazy("New Contact")

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'created_by': self.request.user
        }


class PersonUpdateViewPopout(AuthorRequiredMixin, CommonPopoutUpdateView):
    model = ml_models.Person
    form_class = forms.PersonForm
    parent_crumb = {"title": gettext_lazy("Person"), "url": reverse_lazy("maret:person_list")}
    template_name = 'shared_models/generic_popout_form.html'
    h1 = gettext_lazy("Contact")

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }


class PersonDeleteView(AdminRequiredMixin, CommonDeleteView):
    model = ml_models.Person
    template_name = 'maret/confirm_delete.html'
    success_url = reverse_lazy('maret:person_list')
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Contacts"), "url": reverse_lazy("maret:person_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:person_detail", args=[self.get_object().id])}

    def delete(self, request, *args, **kwargs):
        obj = ml_models.Person.objects.get(pk=kwargs['pk'])
        if obj.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:person_detail", args=[obj.pk, ]))

        return super().delete(request, *args, **kwargs)


#######################################################
# Interactions
#######################################################
class InteractionListView(UserRequiredMixin, CommonFilterView):
    template_name = 'maret/maret_list.html'
    filterset_class = filters.InteractionFilter
    model = models.Interaction
    field_list = [
        {"name": 'description', "class": "", "width": ""},
        {"name": 'interaction_type', "class": "", "width": ""},
        {"name": 'main_topics', "class": "", "width": ""},
        {"name": 'date_of_meeting', "class": "", "width": ""},
    ]
    new_object_url_name = "maret:interaction_new"
    row_object_url_name = "maret:interaction_detail"
    home_url_name = "maret:index"


class InteractionCreateView(AuthorRequiredMixin, CommonCreateView):
    model = models.Interaction
    form_class = forms.InteractionForm
    parent_crumb = {"title": gettext_lazy("Interaction"), "url": reverse_lazy("maret:interaction_list")}
    template_name = "maret/form.html"
    h1 = gettext_lazy("New Interaction")

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'created_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scripts'] = ['maret/js/interactionForm.html']
        return context


class InteractionDetailView(UserRequiredMixin, CommonDetailView):
    model = models.Interaction
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Interactions"), "url": reverse_lazy("maret:interaction_list")}
    container_class = "container-fluid"

    def get_h1(self):
        return self.object.description

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'interaction_type',
            'committee',
            'dfo_role',
            'dfo_liaison',
            'other_dfo_participants',
            'date_of_meeting',
            'main_topic',
            'species',
            'action_items',
            'comments',
            'external_organization',
        ]

        return context


class InteractionDeleteView(AuthorRequiredMixin, CommonDeleteView):
    model = models.Interaction
    success_url = reverse_lazy('maret:interaction_list')
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Committee"), "url": reverse_lazy("maret:interaction_list")}
    template_name = "maret/confirm_delete.html"
    delete_protection = False

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:interaction_detail", args=[self.get_object().id])}


class InteractionUpdateView(AuthorRequiredMixin, CommonUpdateView):
    model = models.Interaction
    form_class = forms.InteractionForm
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Interaction"),
                         "url": reverse_lazy("maret:interaction_list")}
    template_name = "maret/form.html"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:interaction_detail", args=[self.get_object().id])}

    def get_initial(self):
        return {'last_modified_by': self.request.user}


#######################################################
# Committee / Working Groups
#######################################################
class CommitteeListView(UserRequiredMixin, CommonFilterView):
    template_name = 'maret/maret_list.html'
    filterset_class = filters.CommitteeFilter
    model = models.Committee
    field_list = [
        {"name": 'name', "class": "", "width": ""},
    ]
    new_object_url_name = "maret:committee_new"
    row_object_url_name = "maret:committee_detail"
    home_url_name = "maret:index"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scripts'] = ['maret/js/divisionFilter.html']
        return context


class CommitteeCreateView(UserRequiredMixin, CommonCreateView):
    model = models.Committee
    form_class = forms.CommitteeForm
    parent_crumb = {"title": gettext_lazy("Committees"), "url": reverse_lazy("maret:committee_list")}
    template_name = "maret/form.html"
    h1 = gettext_lazy("New Committee")

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'created_by': self.request.user
        }


class CommitteeDetailView(UserRequiredMixin, CommonDetailView):
    model = models.Committee
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Committee / Working Group"), "url": reverse_lazy("maret:committee_list")}
    container_class = "container-fluid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name',
            'branch',
            'division',
            'is_dfo_chair',
            'dfo_liaison',
            'other_dfo_branch',
            'first_nation_participation',
            'provincial_participation',
            'meeting_frequency',
            'are_tor',
            'location_of_tor',
            'main_actions',
            'comments',
        ]

        return context


class CommitteeDeleteView(AuthorRequiredMixin, CommonDeleteView):
    model = models.Committee
    success_url = reverse_lazy('maret:committee_list')
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Committee"), "url": reverse_lazy("maret:committee_list")}
    template_name = "maret/confirm_delete.html"
    delete_protection = False

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:committee_detail", args=[self.get_object().id])}


class CommitteeUpdateView(AuthorRequiredMixin, CommonUpdateView):
    model = models.Committee
    form_class = forms.CommitteeForm
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Committees / Working Groups"),
                         "url": reverse_lazy("maret:committee_list")}
    template_name = "maret/form.html"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:committee_detail", args=[self.get_object().id])}

    def get_initial(self):
        return {'last_modified_by': self.request.user}


#######################################################
# Organization
#######################################################
class OrganizationListView(UserRequiredMixin, CommonFilterView):
    template_name = 'maret/maret_list.html'
    queryset = ml_models.Organization.objects.all().distinct().annotate(
        search_term=Concat(
            'name_eng', Value(" "),
            'abbrev', Value(" "),
            'name_ind', Value(" "),
            'former_name', Value(" "),
            'province__name', Value(" "),
            'province__nom', Value(" "),
            'province__abbrev_eng', Value(" "),
            'province__abbrev_fre', output_field=TextField()))
    filterset_class = filters.OrganizationFilter
    paginate_by = 25
    field_list = [
        {"name": 'name_eng', "class": "", "width": ""},
        {"name": 'name_ind', "class": "", "width": ""},
        {"name": 'abbrev', "class": "", "width": ""},
        {"name": 'province', "class": "", "width": ""},
        {"name": 'grouping', "class": "", "width": "200px"},
        {"name": 'full_address|' + str(_("Full address")), "class": "", "width": "300px"},
        {"name": 'Audio recording|{}'.format(_("Audio recording")), "class": "", "width": ""},
    ]
    home_url_name = "maret:index"
    new_object_url_name = "maret:org_new"
    row_object_url_name = "maret:org_detail"
    container_class = "container-fluid"


class OrganizationCreateView(AuthorRequiredMixin, CommonCreateView):
    model = ml_models.Organization
    template_name = 'maret/form.html'
    form_class = forms.OrganizationForm
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Organizations"), "url": reverse_lazy("maret:org_list")}
    is_multipart_form_data = True
    h1 = gettext_lazy("New Organization")

    def form_valid(self, form):
        object = form.save(commit=False)
        object.last_modified_by = self.request.user
        super().form_valid(form)

        ext_org = None
        fields = form.cleaned_data
        if fields['area']:
            if not ext_org:
                ext_org = models.OrganizationExtension(organization=object)
                ext_org.save()
            ext_org.area.set(fields['area'])
            ext_org.save()

        return HttpResponseRedirect(reverse_lazy('maret:org_detail', kwargs={'pk': object.id}))


class OrganizationDetailView(UserRequiredMixin, CommonDetailView):
    model = ml_models.Organization
    template_name = 'maret/organization_detail.html'
    field_list = [
        'name_eng',
        'name_ind',
        'former_name',
        'abbrev',
        'address',
        'mailing_address',
        'city',
        'postal_code',
        'province',
        'phone',
        'fax',
        'grouping',
        'regions',
        'sectors',
        'dfo_contact_instructions',
        'relationship_rating',
        'orgs',
        'nation',
        'website',
        'council_quorum',
        'next_election',
        'new_coucil_effective_date',
        'election_term',
        'population_on_reserve',
        'population_off_reserve',
        'population_other_reserve',
        'fin',
        'processing_plant',
        'wharf',
        'reserves',
        "metadata|{}".format(gettext_lazy("metadata")),
    ]
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Organizations"), "url": reverse_lazy("maret:org_list")}
    container_class = "container-fluid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class OrganizationUpdateView(AuthorRequiredMixin, CommonUpdateView):
    model = ml_models.Organization
    template_name = 'maret/form.html'
    form_class = forms.OrganizationForm
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Organizations"), "url": reverse_lazy("maret:org_list")}
    is_multipart_form_data = True

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:org_detail", args=[self.get_object().id])}

    def get_initial(self):
        areas = []
        if models.OrganizationExtension.objects.filter(organization=self.object):
            ext_org = models.OrganizationExtension.objects.get(organization=self.object)
            if ext_org:
                areas = [a.pk for a in ext_org.area.all()]

        return {
            'last_modified_by': self.request.user,
            'area': areas,
        }

    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:org_detail", args=[obj.pk, ]))

        obj.save()

        ext_org = None
        if models.OrganizationExtension.objects.filter(organization=obj):
            ext_org = models.OrganizationExtension.objects.get(organization=obj)

        fields = form.cleaned_data
        if fields['area']:
            if not ext_org:
                ext_org = models.OrganizationExtension(organization=obj)
                ext_org.save()
            ext_org.area.set(fields['area'])
            ext_org.save()

        return super().form_valid(form)


class OrganizationDeleteView(AdminRequiredMixin, CommonDeleteView):
    model = ml_models.Organization
    template_name = 'maret/confirm_delete.html'
    success_url = reverse_lazy('maret:org_list')
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Organizations"), "url": reverse_lazy("maret:org_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:org_detail", args=[self.get_object().id])}

    def delete(self, request, *args, **kwargs):
        obj = ml_models.Organization.objects.get(pk=kwargs['pk'])
        if obj.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:org_detail", args=[obj.pk, ]))

        return super().delete(request, *args, **kwargs)



#######################################################
# Organization Memberships
#######################################################
class MemberCreateView(AuthorRequiredMixin, CommonPopoutCreateView):
    model = ml_models.OrganizationMember
    template_name = 'maret/member_form_popout.html'
    form_class = forms.MemberForm
    width = 1000
    height = 700
    h1 = gettext_lazy("New Organization Member")

    def get_initial(self):
        org = ml_models.Organization.objects.get(pk=self.kwargs['org'])
        return {
            'organization': org,
            'last_modified_by': self.request.user,
        }

    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.organization.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:org_detail", args=[obj.organization.pk, ]))

        obj.save()
        return HttpResponseRedirect(reverse("ihub:member_edit", args=[obj.id]))


class MemberUpdateView(AuthorRequiredMixin, CommonPopoutUpdateView):
    model = ml_models.OrganizationMember
    template_name = 'maret/member_form_popout.html'
    form_class = forms.MemberForm
    width = 1000
    height = 800

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }

    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.organization.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:org_detail", args=[obj.organization.pk, ]))

        obj.save()
        return HttpResponseRedirect(self.get_success_url())


class MemberDeleteView(AdminRequiredMixin, CommonPopoutDeleteView):
    model = ml_models.OrganizationMember

    def delete(self, request, *args, **kwargs):
        obj = ml_models.OrganizationMember.objects.get(pk=kwargs['pk'])
        if obj.organization.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:person_detail", args=[obj.pk, ]))

        return super().delete(request, *args, **kwargs)


class CommonMaretFormset(AdminRequiredMixin, CommonFormsetView):
    template_name = 'maret/formset.html'
    home_url_name = "maret:index"


class TopicFormsetView(CommonMaretFormset):
    h1 = _("Manage Discussion Topics")
    queryset = models.DiscussionTopic.objects.all()
    formset_class = forms.TopicFormSet
    success_url_name = "maret:manage_topics"
    # delete_url_name = "maret:delete_topics"


class SpeciesFormsetView(CommonMaretFormset):
    h1 = _("Manage Species")
    queryset = models.Species.objects.all()
    formset_class = forms.SpeciesFormSet
    success_url_name = "maret:manage_species"


class AreaFormsetView(CommonMaretFormset):
    h1 = _("Manage Areas")
    queryset = models.Area.objects.all()
    formset_class = forms.AreaFormSet
    success_url_name = "maret:manage_areas"
