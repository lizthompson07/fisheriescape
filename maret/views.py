from shared_models.views import CommonTemplateView, CommonFilterView

from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from django.db.models import TextField, Value
from django.db.models.functions import Concat

from maret.utils import UserRequiredMixin
from maret import models, filters

from masterlist import models as ml_models


class IndexView(UserRequiredMixin, CommonTemplateView):
    h1 = "home"
    template_name = 'maret/index.html'

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, mark_safe(_("Please note that only <b>unclassified information</b> may be entered into this application.")))
        return super().dispatch(request, *args, **kwargs)


class EntryListView(UserRequiredMixin, CommonFilterView):
    template_name = "maret/entry_list.html"
    model = models.Entry
    filterset_class = filters.EntryFilter
    paginate_by = 100
    field_list = [
        {"name": 'title', "class": "", "width": "400px"},
        {"name": 'entry_type', "class": "", "width": ""},
        {"name": 'regions', "class": "", "width": ""},
        {"name": 'organizations', "class": "", "width": "400px"},
        {"name": 'sectors', "class": "", "width": "200px"},
        {"name": 'status', "class": "", "width": "170px"},
    ]
    # new_object_url_name = "maret:entry_new"
    # row_object_url_name = "maret:entry_detail"
    home_url_name = "maret:index"
    h1 = _("Entries")
    container_class = "container-fluid"
    open_row_in_new_tab = True


class OrganizationListView(UserRequiredMixin, CommonFilterView):
    template_name = 'maret/organization_list.html'
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
    # new_object_url_name = "maret:org_new"
    # row_object_url_name = "maret:org_detail"
    container_class = "container-fluid"


class PersonListView(UserRequiredMixin, CommonFilterView):
    template_name = 'maret/person_list.html'
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
