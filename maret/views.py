from shared_models.views import CommonTemplateView, CommonFilterView, CommonCreateView, CommonFormsetView

from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils.translation import gettext as _, gettext_lazy
from django.utils.safestring import mark_safe
from django.db.models import TextField, Value
from django.db.models.functions import Concat

from django.urls import reverse_lazy

from maret.utils import UserRequiredMixin
from maret import models, filters, forms

from masterlist import models as ml_models


class IndexView(UserRequiredMixin, CommonTemplateView):
    h1 = "home"
    template_name = 'maret/index.html'

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, mark_safe(_("Please note that only <b>unclassified information</b> may be entered into this application.")))
        return super().dispatch(request, *args, **kwargs)


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
    # row_object_url_name = "maret:org_detail"
    container_class = "container-fluid"


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
    # new_object_url_name = "maret:person_new"
    # row_object_url_name = "maret:person_detail"
    home_url_name = "maret:index"
    paginate_by = 100
    h1 = _("Contacts")
    container_class = "container-fluid"


class InteractionListView(UserRequiredMixin, CommonFilterView):
    template_name = 'maret/maret_list.html'
    filterset_class = filters.InteractionFilter
    model = models.Interaction
    field_list = [
        {"name": 'interaction_type', "class": "", "width": ""},
        {"name": 'main_topics', "class": "", "width": ""},
        {"name": 'date_of_meeting', "class": "", "width": ""},
    ]
    new_object_url_name = "maret:interaction_new"


class CommitteeListView(UserRequiredMixin, CommonFilterView):
    template_name = 'maret/maret_list.html'
    filterset_class = filters.CommitteeFilter
    model = models.Committee
    field_list = [
        {"name": 'name', "class": "", "width": ""},
    ]
    new_object_url_name = "maret:committee_new"


class CommitteeCreateView(UserRequiredMixin, CommonCreateView):
    model = models.Committee
    form_class = forms.CommitteeCreateForm
    parent_crumb = {"title": gettext_lazy("Committees"), "url": reverse_lazy("maret:committee_list")}
    template_name = "maret/form.html"
    h1 = gettext_lazy("New Committee")

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'created_by': self.request.user
        }


class OrganizationCreateView(UserRequiredMixin, CommonCreateView):
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
        object.locked_by_ihub = True
        super().form_valid(form)
        return HttpResponseRedirect(reverse_lazy('maret:org_detail', kwargs={'pk': object.id}))


class InteractionCreateView(UserRequiredMixin, CommonCreateView):
    model = models.Interaction
    form_class = forms.InteractionCreateForm
    parent_crumb = {"title": gettext_lazy("Interaction"), "url": reverse_lazy("maret:interaction_list")}
    template_name = "maret/form.html"
    h1 = gettext_lazy("New Interaction")

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'created_by': self.request.user
        }


class TopicFormsetView(UserRequiredMixin, CommonFormsetView):
    template_name = 'maret/formset.html'
    h1 = _("Manage Discussion Topics")
    queryset = models.DiscussionTopic.objects.all()
    formset_class = forms.TopicFormSet
    success_url_name = "maret:manage_topics"
    home_url_name = "maret:index"
    # delete_url_name = "maret:delete_topics"


class SpeciesFormsetView(UserRequiredMixin, CommonFormsetView):
    template_name = 'maret/formset.html'
    h1 = _("Manage Species")
    queryset = models.Species.objects.all()
    formset_class = forms.SpeciesFormSet
    success_url_name = "maret:manage_species"
    home_url_name = "maret:index"