import math

from shared_models.views import CommonTemplateView, CommonFilterView, CommonCreateView, CommonFormsetView, \
    CommonDetailView, CommonDeleteView, CommonUpdateView, CommonPopoutUpdateView, CommonPopoutCreateView, \
    CommonPopoutDeleteView, CommonHardDeleteView

from django.contrib import messages
from django.http import HttpResponseRedirect

from django.utils import timezone
from django.utils.translation import gettext as _, gettext_lazy
from django.utils.safestring import mark_safe

from django.db.models import TextField, Value
from django.db.models.functions import Concat

from django.urls import reverse_lazy, reverse

from maret.utils import UserRequiredMixin, AuthorRequiredMixin, AdminRequiredMixin
from maret import models, filters, forms, utils

from masterlist import models as ml_models

from easy_pdf.views import PDFTemplateView


#######################################################
# Application Help text controls
#######################################################
class CommonCreateViewHelp(CommonCreateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = utils.get_help_text_dict(self.model)

        # if the UserMode table has this user in "edit" mode provide the
        # link to the dialog to manage help text via the manage_help_url
        # and provide the model name the help text will be assigned to.
        # The generic_form_with_help_text.html from the shared_models app
        # will provide the field name and together you have the required
        # model and field needed to make an entry in the Help Text table.
        if models.UserMode.objects.filter(user=self.request.user) and models.UserMode.objects.get(user=self.request.user).mode == 2:
            context['manage_help_url'] = "maret:manage_help_text"
            context['model_name'] = self.model.__name__

        return context


# This is the dialog presented to the user to enter help text for a given model/field
# it uses the Create View to both create entries and update them. Accessed via the manage_help_url.
#
# A point of failure may be if the (model, field_name) pair is not unique in the help text table.
class HelpTextPopView(AdminRequiredMixin, CommonCreateView):
    model = models.HelpText
    form_class = forms.HelpTextPopForm
    success_url = reverse_lazy("shared_models:close_me")
    title = gettext_lazy("Update Help Text")

    def get_initial(self):
        if self.model.objects.filter(model=self.kwargs['model_name'], field_name=self.kwargs['field_name']):
            obj = self.model.objects.get(model=self.kwargs['model_name'], field_name=self.kwargs['field_name'])
            return {
                'model': self.kwargs['model_name'],
                'field_name': self.kwargs['field_name'],
                'eng_text': obj.eng_text,
                'fra_text': obj.fra_text
            }

        return {
            'model': self.kwargs['model_name'],
            'field_name': self.kwargs['field_name'],
        }

    def form_valid(self, form):
        if self.model.objects.filter(model=self.kwargs['model_name'], field_name=self.kwargs['field_name']):
            data = form.cleaned_data
            obj = self.model.objects.get(model=self.kwargs['model_name'], field_name=self.kwargs['field_name'])
            obj.eng_text = data['eng_text']
            obj.fra_text = data['fra_text']
            obj.save()
            return HttpResponseRedirect(reverse_lazy("shared_models:close_me"))
        else:
            return super().form_valid(form)


# Controls the administrative helptext page that allows all entries to be viewed, modified and deleted
class HelpTextFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'maret/formset.html'
    title = _("MarET Help Text")
    h1 = _("Manage Help Texts")
    queryset = models.HelpText.objects.all()
    formset_class = forms.HelpTextFormset
    success_url_name = "maret:manage_help_texts"
    home_url_name = "maret:index"
    delete_url_name = "maret:delete_help_text"


class HelpTextHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.HelpText
    success_url = reverse_lazy("maret:manage_help_texts")


#######################################################
# Home page view
#######################################################
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


class PersonCreateView(AuthorRequiredMixin, CommonCreateViewHelp):
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

    def form_valid(self, form):
        object = form.save(commit=False)
        object.last_modified_by = self.request.user
        super().form_valid(form)

        ext_con = None
        fields = form.cleaned_data
        if fields['role']:
            if not ext_con:
                ext_con = models.ContactExtension(contact=object)
                ext_con.save()
            ext_con.role = fields['role']
            ext_con.save()

        return HttpResponseRedirect(reverse_lazy('maret:person_detail', kwargs={'pk': object.id}))


class PersonUpdateView(AuthorRequiredMixin, CommonUpdateView):
    model = ml_models.Person
    form_class = forms.PersonForm
    parent_crumb = {"title": gettext_lazy("Person"), "url": reverse_lazy("maret:person_list")}
    template_name = "maret/form.html"
    h1 = gettext_lazy("Contact")

    def get_initial(self):
        role = None
        if models.ContactExtension.objects.filter(contact=self.object):
            ext_cont = models.ContactExtension.objects.get(contact=self.object)
            if ext_cont:
                role = ext_cont.role

        return {
            'last_modified_by': self.request.user,
            'role': role,
        }

    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:person_detail", args=[obj.pk, ]))

        obj.save()

        ext_con = None
        if models.ContactExtension.objects.filter(contact=obj):
            ext_con = models.ContactExtension.objects.get(contact=obj)

        fields = form.cleaned_data
        if fields['role']:
            if not ext_con:
                ext_con = models.ContactExtension(organization=obj)
                ext_con.save()
            ext_con.role = fields['role']
            ext_con.save()

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


class InteractionCreateView(AuthorRequiredMixin, CommonCreateViewHelp):
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
            'last_modified',
            'last_modified_by',
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


#######################################################
# Committee / Working Groups
#######################################################
class CommitteeListView(UserRequiredMixin, CommonFilterView):
    h1 = gettext_lazy("Committees / Working Groups")
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


class CommitteeCreateView(UserRequiredMixin, CommonCreateViewHelp):
    model = models.Committee
    form_class = forms.CommitteeForm
    parent_crumb = {"title": gettext_lazy("Committees / Working Groups"), "url": reverse_lazy("maret:committee_list")}
    template_name = "maret/form.html"
    h1 = gettext_lazy("Committees / Working Groups")

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'created_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scripts'] = ['maret/js/divisionFilter.html']
        return context


class CommitteeDetailView(UserRequiredMixin, CommonDetailView):
    model = models.Committee
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Committees / Working Groups"), "url": reverse_lazy("maret:committee_list")}
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
    grandparent_crumb = {"title": gettext_lazy("Committees / Working Groups"), "url": reverse_lazy("maret:committee_list")}
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
    h1 = gettext_lazy("Committees / Working Groups")
    template_name = "maret/form.html"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:committee_detail", args=[self.get_object().id])}

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scripts'] = ['maret/js/divisionFilter.html']
        return context


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


class OrganizationCreateView(AuthorRequiredMixin, CommonCreateViewHelp):
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

        if fields['category']:
            if not ext_org:
                ext_org = models.OrganizationExtension(organization=object)
                ext_org.save()
            ext_org.category.set(fields['category'])
            ext_org.save()

        if fields['asc_province']:
            if not ext_org:
                ext_org = models.OrganizationExtension(organization=object)
                ext_org.save()
            ext_org.associated_provinces.set(fields['asc_province'])
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
        category = []
        asc_province = []
        if models.OrganizationExtension.objects.filter(organization=self.object):
            ext_org = models.OrganizationExtension.objects.get(organization=self.object)
            if ext_org:
                areas = [a.pk for a in ext_org.area.all()]
                category = [c.pk for c in ext_org.category.all()]
                asc_province = [p.pk for p in ext_org.associated_provinces.all()]

        return {
            'last_modified_by': self.request.user,
            'area': areas,
            'category': category,
            'asc_province': asc_province,
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

        if fields['category']:
            if not ext_org:
                ext_org = models.OrganizationExtension(organization=obj)
                ext_org.save()
            ext_org.category.set(fields['category'])
            ext_org.save()

        if fields['asc_province']:
            if not ext_org:
                ext_org = models.OrganizationExtension(organization=object)
                ext_org.save()
            ext_org.associated_provinces.set(fields['asc_province'])
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


class OrganizationCueCard(PDFTemplateView):
    template_name = "maret/report_cue_card.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = ml_models.Organization.objects.get(pk=self.kwargs["org"])
        context["org"] = org

        context["org_field_list_1"] = [
            'name_eng',
            'name_ind',
            'former_name',
            'abbrev',
            'nation',
            'website',
        ]
        context["org_field_list_2"] = [
            'address',
            'mailing_address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
        ]
        context["org_field_list_3"] = [
            'next_election',
            'election_term',
            'new_coucil_effective_date',
            'population_on_reserve',
            'population_off_reserve',
            'population_other_reserve',
            'relationship_rating',
        ]
        context["org_field_list_4"] = [
            'fin',
            'processing_plant',
            'wharf',
            'dfo_contact_instructions',
            'council_quorum',
            'reserves',
            'orgs',
            'notes',
        ]

        # determine how many rows for the table
        context["contact_table_rows"] = range(0, math.ceil(org.members.count() / 4))
        context["one_to_four"] = range(0, 4)

        context["entry_field_list_1"] = [
            'fiscal_year',
            'initial_date',
            'anticipated_end_date',
            'status',
        ]
        context["entry_field_list_2"] = [
            'sectors',
            'entry_type',
            'regions',
        ]
        context["entry_field_list_3"] = [
            'funding_program',
            'funding_needed',
            'funding_purpose',
            'amount_requested',
        ]
        context["entry_field_list_4"] = [
            'amount_approved',
            'amount_transferred',
            'amount_lapsed',
        ]
        context["entry_field_list_5"] = [
            'amount_owing',
        ]
        context["now"] = timezone.now()
        return context


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


class OrgCategoriesFormsetView(CommonMaretFormset):
    h1 = _("Manage Organization Categories")
    queryset = models.OrgCategory.objects.all()
    formset_class = forms.OrgCategoriesFormSet
    success_url_name = "maret:manage_org_categories"
