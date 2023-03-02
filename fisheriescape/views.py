from copy import deepcopy

from django.conf import settings
from django.utils.translation import gettext as _, gettext_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import TextField, Value
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView
from django_filters.views import FilterView
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from shared_models.views import CommonFilterView, CommonCreateView, CommonDetailView, CommonUpdateView, \
    CommonDeleteView, CommonHardDeleteView, CommonFormsetView, CommonTemplateView
from . import models
from . import forms
from . import filters

import json
from django.core.serializers import serialize

from .api.serializers import ScoreSerializer


class CloserTemplateView(TemplateView):
    template_name = 'fisheriescape/close_me.html'


### Permissions ###


class FisheriescapeAccessRequired(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=fisheriescape')
        return super().dispatch(request, *args, **kwargs)


def in_fisheriescape_admin_group(user):
    if "fisheriescape_admin" in [g.name for g in user.groups.all()]:
        return True


class FisheriescapeAdminAccessRequired(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_fisheriescape_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=fisheriescape')
        return super().dispatch(request, *args, **kwargs)


def in_fisheriescape_edit_group(user):
    """this group includes the admin group so there is no need to add an admin to this group"""
    if user:
        if in_fisheriescape_admin_group(user) or user.groups.filter(name='fisheriescape_edit').count() != 0:
            return True


class FisheriescapeEditRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_fisheriescape_edit_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=fisheriescape')
        return super().dispatch(request, *args, **kwargs)


class IndexView(FisheriescapeAccessRequired, CommonTemplateView):
    h1 = "home"
    template_name = 'fisheriescape/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["fisheriescape_admin"] = get_object_or_404(Group, name="fisheriescape_admin")
        context["fisheriescape_edit"] = get_object_or_404(Group, name="fisheriescape_edit")
        return context


## ADMIN USER ACCESS CONTROL ##


class UserListView(FisheriescapeAdminAccessRequired, CommonFilterView):
    template_name = "fisheriescape/user_list.html"
    filterset_class = filters.UserFilter
    home_url_name = "index"
    paginate_by = 25
    h1 = "Fisheriescape App User List"
    field_list = [
        {"name": 'first_name', "class": "", "width": ""},
        {"name": 'last_name', "class": "", "width": ""},
        {"name": 'email', "class": "", "width": ""},
        {"name": 'last_login|{}'.format(gettext_lazy("Last login to DM Apps")), "class": "", "width": ""},
    ]
    new_object_url = reverse_lazy("shared_models:user_new")

    def get_queryset(self):
        queryset = User.objects.order_by("first_name", "last_name").annotate(
            search_term=Concat('first_name', Value(""), 'last_name', Value(""), 'email', output_field=TextField())
        )
        if self.kwargs.get("fisheriescape"):
            queryset = queryset.filter(groups__name__icontains="fisheriescape").distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["fisheriescape_admin"] = get_object_or_404(Group, name="fisheriescape_admin")
        context["fisheriescape_edit"] = get_object_or_404(Group, name="fisheriescape_edit")
        return context


@login_required(login_url='/accounts/login/')
@user_passes_test(in_fisheriescape_admin_group, login_url='/accounts/denied/')
def toggle_user(request, pk, type):
    my_user = User.objects.get(pk=pk)
    fisheriescape_admin = get_object_or_404(Group, name="fisheriescape_admin")
    fisheriescape_edit = get_object_or_404(Group, name="fisheriescape_edit")
    if type == "admin":
        # if the user is in the admin group, remove them
        if fisheriescape_admin in my_user.groups.all():
            my_user.groups.remove(fisheriescape_admin)
        # otherwise add them
        else:
            my_user.groups.add(fisheriescape_admin)
    elif type == "edit":
        # if the user is in the edit group, remove them
        if fisheriescape_edit in my_user.groups.all():
            my_user.groups.remove(fisheriescape_edit)
        # otherwise add them
        else:
            my_user.groups.add(fisheriescape_edit)
    return HttpResponseRedirect("{}#user_{}".format(request.META.get('HTTP_REFERER'), my_user.id))

### SETTINGS ###
### FORMSETS ###


class MarineMammalFormsetView(FisheriescapeAdminAccessRequired, CommonFormsetView):
    template_name = 'fisheriescape/formset.html'
    h1 = "Manage Marine Mammals"
    queryset = models.MarineMammal.objects.all()
    formset_class = forms.MarineMammalFormSet
    success_url_name = "fisheriescape:manage_marinemammals"
    home_url_name = "fisheriescape:index"
    delete_url_name = "fisheriescape:delete_marinemammals"
    container_class = "container-fluid"


class MarineMammalHardDeleteView(FisheriescapeAdminAccessRequired, CommonHardDeleteView):
    model = models.MarineMammal
    success_url = reverse_lazy("fisheriescape:manage_marinemammals")


class SpeciesFormsetView(FisheriescapeAdminAccessRequired, CommonFormsetView):
    template_name = 'fisheriescape/formset.html'
    h1 = "Manage Fishery Species"
    queryset = models.Species.objects.all()
    formset_class = forms.SpeciesFormSet
    success_url_name = "fisheriescape:manage_species"
    home_url_name = "fisheriescape:index"
    delete_url_name = "fisheriescape:delete_species"
    container_class = "container-fluid"


class SpeciesHardDeleteView(FisheriescapeAdminAccessRequired, CommonHardDeleteView):
    model = models.Species
    success_url = reverse_lazy("fisheriescape:manage_species")


# #
# # # MAP #
# # ###########
# #
#

# class MapView(FisheriescapeAccessRequired, TemplateView):
#     template_name = "fisheriescape/map.html"
#
#     def get_context_data(self, **kwargs):
#         """Return the view context data."""
#         context = super().get_context_data(**kwargs)
#         context["lobster_areas"] = serialize("geojson", models.FisheryArea.objects.filter(layer_id="Lobster"))
#         context["snow_crab_areas"] = serialize("geojson", models.FisheryArea.objects.filter(layer_id="Crab"))
#         context["herring_areas"] = serialize("geojson", models.FisheryArea.objects.filter(layer_id="Herring"))
#         context["groundfish_areas"] = serialize("geojson", models.FisheryArea.objects.filter(layer_id="Groundfish"))
#         context["nafo_sub_areas"] = serialize("geojson", models.FisheryArea.objects.filter(layer_id="NAFO Subareas"))
#         context["nafo_areas"] = serialize("geojson", models.NAFOArea.objects.filter(layer_id="NAFO"))
#         context["mapbox_api_key"] = settings.MAPBOX_API_KEY
#         return context


# #
# # # FISHERY AREA #
# # ###########
# #
#


class FisheryAreaListView(FisheriescapeAccessRequired, CommonFilterView):
    template_name = "fisheriescape/list.html"
    filterset_class = filters.FisheryAreaFilter
    h1 = "Fishery Area List"
    home_url_name = "fisheriescape:index"
    row_object_url_name = "fisheriescape:fishery_area_detail"
    # new_btn_text = "New Fishery Area"

    queryset = models.FisheryArea.objects.annotate(
        search_term=Concat('name', 'id', output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'layer_id', "class": "", "width": ""},
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nafo_area', "class": "", "width": ""},
        {"name": 'region', "class": "", "width": ""},
    ]

    # def get_new_object_url(self):
    #     return reverse("fisheriescape:fishery_area_new", kwargs=self.kwargs)


class FisheryAreaDetailView(FisheriescapeAdminAccessRequired, CommonDetailView):
    model = models.FisheryArea
    field_list = [
        'id',
        'layer_id',
        'name',
        'nafo_area',
        'region',

    ]
    home_url_name = "fisheriescape:index"
    parent_crumb = {"title": gettext_lazy("Fishery Area List"), "url": reverse_lazy("fisheriescape:fishery_area_list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # contexts for _fishery.html file
        context["random_fishery"] = models.Fishery.objects.first()
        context["fishery_field_list"] = [
            'species',
            'start_date',
            'end_date',
            'participant_detail',
            'fishery_status',
            'gear_type',
        ]

        # contexts for fishery_detail maps
        polygon_subset = models.FisheryArea.objects.filter(name=self.object)

        context["fishery_polygons"] = serialize("geojson", polygon_subset)
        context["mapbox_api_key"] = settings.MAPBOX_API_KEY

        return context


# class FisheryAreaUpdateView(FisheriescapeAdminAccessRequired, CommonUpdateView):
#     model = models.FisheryArea
#     form_class = forms.FisheryAreaForm
#     template_name = 'fisheriescape/geo_form.html'
#     cancel_text = _("Cancel")
#     home_url_name = "fisheriescape:index"
#
#     def form_valid(self, form):
#         my_object = form.save()
#         messages.success(self.request, _(f"Fishery Area record successfully updated for : {my_object}"))
#         return HttpResponseRedirect(reverse("fisheriescape:fishery_area_detail", kwargs=self.kwargs))
#
#     def get_active_page_name_crumb(self):
#         my_object = self.get_object()
#         return my_object
#
#     def get_h1(self):
#         my_object = self.get_object()
#         return my_object
#
#     def get_parent_crumb(self):
#         return {"title": str(self.get_object()),
#                 "url": reverse_lazy("fisheriescape:fishery_area_detail", kwargs=self.kwargs)}
#
#     def get_grandparent_crumb(self):
#         kwargs = deepcopy(self.kwargs)
#         del kwargs["pk"]
#         return {"title": _("Fishery Area List"), "url": reverse("fisheriescape:fishery_area_list", kwargs=kwargs)}
#
#
# class FisheryAreaCreateView(FisheriescapeAdminAccessRequired, CommonCreateView):
#     model = models.FisheryArea
#     form_class = forms.FisheryAreaForm2
#     template_name = 'fisheriescape/form.html'
#     home_url_name = "fisheriescape:index"
#     h1 = gettext_lazy("Add New Fishery Area")
#     parent_crumb = {"title": gettext_lazy("Fishery Area List"), "url": reverse_lazy("fisheriescape:fishery_area_list")}
#
#     def form_valid(self, form):
#         my_object = form.save()
#         messages.success(self.request, _(f"Fishery Area record successfully created for : {my_object}"))
#         return super().form_valid(form)
#
#
# class FisheryAreaDeleteView(FisheriescapeAdminAccessRequired, CommonDeleteView):
#     model = models.FisheryArea
#     permission_required = "__all__"
#     success_url = reverse_lazy('fisheriescape:fishery_area_list')
#     template_name = 'fisheriescape/confirm_delete.html'
#     home_url_name = "fisheriescape:index"
#     grandparent_crumb = {"title": gettext_lazy("Fishery Area List"),
#                          "url": reverse_lazy("fisheriescape:fishery_area_list")}
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object(), "url": reverse_lazy("fisheriescape:fishery_area_detail", kwargs=self.kwargs)}

# #
# # # NAFO AREA #
# # ###########
# #
#


class NAFOAreaListView(FisheriescapeAccessRequired, CommonFilterView):
    template_name = "fisheriescape/list.html"
    filterset_class = filters.NAFOAreaFilter
    h1 = "NAFO Area List"
    home_url_name = "fisheriescape:index"
    row_object_url_name = "fisheriescape:nafo_area_detail"
    # new_btn_text = "New NAFO Area"

    queryset = models.NAFOArea.objects.annotate(
        search_term=Concat('name', 'id', output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'layer_id', "class": "", "width": ""},
        {"name": 'name', "class": "", "width": ""},
    ]

    # def get_new_object_url(self):
    #     return reverse("fisheriescape:fishery_area_new", kwargs=self.kwargs)


class NAFOAreaDetailView(FisheriescapeAdminAccessRequired, CommonDetailView):
    model = models.NAFOArea
    field_list = [
        'id',
        'layer_id',
        'name',

    ]
    home_url_name = "fisheriescape:index"
    parent_crumb = {"title": gettext_lazy("NAFO Area List"), "url": reverse_lazy("fisheriescape:nafo_area_list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # contexts for _nafofishery.html file
        fishery_area_lookup = models.FisheryArea.objects.filter(nafo_area=self.object)
        fisherys_qs = models.Fishery.objects.filter(fishery_areas__in=fishery_area_lookup)

        context["random_fishery"] = fisherys_qs
        context["fishery_field_list"] = [
            'species',
            'fishery_areas',
            'start_date',
            'end_date',
            'participant_detail',
            'fishery_status',
            'gear_type',
        ]

        # contexts for fishery_detail maps
        polygon_subset = models.NAFOArea.objects.filter(name=self.object)

        context["fishery_polygons"] = serialize("geojson", polygon_subset)
        context["mapbox_api_key"] = settings.MAPBOX_API_KEY

        return context


# #
# # # FISHERY #
# # ###########
# #
#


class FisheryListView(FisheriescapeAccessRequired, CommonFilterView):
    template_name = "fisheriescape/list.html"
    filterset_class = filters.FisheryFilter
    h1 = "Fishery List"
    home_url_name = "fisheriescape:index"
    row_object_url_name = "fisheriescape:fishery_detail"
    new_btn_text = "New Fishery"
    container_class = "container-fluid"

    queryset = models.Fishery.objects.annotate(
        search_term=Concat('species__english_name', 'species__french_name',
                           'species__latin_name', 'fishery_comment',
                           'gear_comment', 'monitoring_comment',
                           'mitigation_comment', output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'start_date', "class": "", "width": ""},
        {"name": 'end_date', "class": "", "width": ""},
        {"name": 'species', "class": "", "width": ""},
        {"name": 'fishery_areas', "class": "", "width": ""},
        {"name": 'participants', "class": "", "width": ""},
        {"name": 'participant_detail', "class": "", "width": ""},
        {"name": 'fishery_status', "class": "", "width": ""},
        {"name": 'gear_type', "class": "", "width": ""},
        {"name": 'management_system', "class": "", "width": ""},
    ]

    def get_new_object_url(self):
        return reverse("fisheriescape:fishery_new", kwargs=self.kwargs)


class FisheryDetailView(FisheriescapeAdminAccessRequired, CommonDetailView):
    model = models.Fishery
    home_url_name = "fisheriescape:index"
    parent_crumb = {"title": gettext_lazy("Fishery List"), "url": reverse_lazy("fisheriescape:fishery_list")}
    container_class = "container-fluid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'species',
            'fishery_areas',
            'nafo_fishery_areas|{}'.format(_("NAFO areas")),
            'participants',
            'participant_detail',
            'start_date',
            'end_date',
            'fishery_status',
            'license_type',
            'management_system',
            'fishery_comment',
            'metadata|{}'.format(_("metadata")),
        ]
        context["field_list_gear"] = [
            'gear_type',
            'gear_amount',
            'gear_config',
            'gear_soak',
            'gear_primary_colour',
            'gear_secondary_colour',
            'gear_tertiary_colour',
            'gear_comment',
        ]
        context["field_list_monitoring"] = [
            'monitoring_aso',
            'monitoring_dockside',
            'monitoring_logbook',
            'monitoring_vms',
            'monitoring_comment',
        ]
        context["field_list_other"] = [
            'mitigation',
            'mitigation_comment',
        ]

        # contexts for _mammals.html file
        context["random_mammals"] = models.MarineMammal.objects.first()
        context["mammals_field_list"] = [
            'english_name',
            'french_name',
            'latin_name',
            'population',
            'sara_status',
            'cosewic_status',
            'website',
        ]

        # contexts for fishery_detail maps
        polygon_subset = models.FisheryArea.objects.filter(fisherys=self.object)  # call related manager with 'fisherys'

        context["fishery_polygons"] = serialize("geojson", polygon_subset)
        context["mapbox_api_key"] = settings.MAPBOX_API_KEY

        return context


class FisheryUpdateView(FisheriescapeAdminAccessRequired, CommonUpdateView):
    model = models.Fishery
    form_class = forms.FisheryForm
    template_name = 'fisheriescape/form.html'
    cancel_text = _("Cancel")
    home_url_name = "fisheriescape:index"

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Fishery record successfully updated for : {my_object}"))
        return HttpResponseRedirect(reverse("fisheriescape:fishery_detail", kwargs=self.kwargs))

    def get_active_page_name_crumb(self):
        my_object = self.get_object()
        return my_object

    def get_h1(self):
        my_object = self.get_object()
        return my_object

    def get_parent_crumb(self):
        return {"title": str(self.get_object()),
                "url": reverse_lazy("fisheriescape:fishery_detail", kwargs=self.kwargs)}

    def get_grandparent_crumb(self):
        kwargs = deepcopy(self.kwargs)
        del kwargs["pk"]
        return {"title": _("Fishery List"), "url": reverse("fisheriescape:fishery_list", kwargs=kwargs)}


class FisheryCreateView(FisheriescapeAdminAccessRequired, CommonCreateView):
    model = models.Fishery
    form_class = forms.FisheryForm
    template_name = 'fisheriescape/form.html'
    home_url_name = "fisheriescape:index"
    h1 = gettext_lazy("Add New Fishery")
    parent_crumb = {"title": gettext_lazy("Fishery List"), "url": reverse_lazy("fisheriescape:fishery_list")}

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Fishery record successfully created for : {my_object}"))
        return super().form_valid(form)


class FisheryDeleteView(FisheriescapeAdminAccessRequired, CommonDeleteView):
    model = models.Fishery
    permission_required = "__all__"
    success_url = reverse_lazy('fisheriescape:fishery_list')
    template_name = 'fisheriescape/confirm_delete.html'
    home_url_name = "fisheriescape:index"
    grandparent_crumb = {"title": gettext_lazy("Fishery List"), "url": reverse_lazy("fisheriescape:fishery_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("fisheriescape:fishery_detail", kwargs=self.kwargs)}


# #
# # # ANALYSES #
# # ###########
# #
#

# class AnalysesFilterView(FisheriescapeAccessRequired, CommonFilterView):
#     template_name = "fisheriescape/analyses_filter.html"
#     filterset_class = filters.AnalysesFilter
#     h1 = "Analyses Search"
#     home_url_name = "fisheriescape:index"
#     # row_object_url_name = "fisheriescape:fishery_detail"
#     new_btn_text = "New Analysis"
#
#     queryset = models.Analyses.objects.annotate(
#         search_term=Concat('species', 'id', output_field=TextField()))
#
#     field_list = [
#         {"name": 'id', "class": "", "width": ""},
#         {"name": 'species', "class": "", "width": ""},
#         {"name": 'type', "class": "", "width": ""},
#         {"name": 'week', "class": "", "width": ""},
#         # {"name": 'image', "class": "", "width": ""},
#         {"name": 'ref_text', "class": "", "width": ""},
#     ]
#
#     def get_new_object_url(self):
#         return reverse("fisheriescape:analyses_new", kwargs=self.kwargs)


class AnalysesCreateView(FisheriescapeAdminAccessRequired, CommonCreateView):
    model = models.Analyses
    form_class = forms.AnalysesForm
    template_name = 'fisheriescape/form.html'
    home_url_name = "fisheriescape:index"
    h1 = gettext_lazy("Add New Analysis")
    # parent_crumb = {"title": gettext_lazy("Analysis Search"), "url": reverse_lazy("fisheriescape:analyses_filter")}
    is_multipart_form_data = True

    def form_valid(self, form):
        # my_object = form.save()
        if form.is_valid():
            my_object = form.save()
        messages.success(self.request, _(f"Analysis record successfully created for : {my_object}"))
        return super().form_valid(form)


class AnalysesUpdateView(FisheriescapeAdminAccessRequired, CommonUpdateView):
    model = models.Analyses
    form_class = forms.AnalysesForm
    template_name = 'fisheriescape/form.html'
    cancel_text = _("Cancel")
    home_url_name = "fisheriescape:index"
    is_multipart_form_data = True

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Analysis record successfully updated for : {my_object}"))
        return HttpResponseRedirect(reverse("fisheriescape:analyses_detail", kwargs=self.kwargs))

    # def get_active_page_name_crumb(self):
    #     my_object = self.get_object()
    #     return my_object

    def get_h1(self):
        my_object = self.get_object()
        return my_object

    # def get_parent_crumb(self):
    #     return {"title": str(self.get_object()),
    #             "url": reverse_lazy("fisheriescape:fishery_detail", kwargs=self.kwargs)}
    #
    # def get_grandparent_crumb(self):
    #     kwargs = deepcopy(self.kwargs)
    #     del kwargs["pk"]
    #     return {"title": _("Fishery List"), "url": reverse("fisheriescape:fishery_list", kwargs=kwargs)}


class AnalysesDetailView(FisheriescapeAdminAccessRequired, CommonDetailView):
    model = models.Analyses
    field_list = [
        'id',
        'species',
        'type',
        'week',
        'image',
        'ref_text',

    ]
    home_url_name = "fisheriescape:index"
    # parent_crumb = {"title": gettext_lazy("Analyses Search"), "url": reverse_lazy("fisheriescape:analyses_filter")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AnalysesDeleteView(FisheriescapeAdminAccessRequired, CommonDeleteView):
    model = models.Analyses
    permission_required = "__all__"
    # success_url = reverse_lazy('fisheriescape:analyses_filter')
    template_name = 'fisheriescape/confirm_delete.html'
    home_url_name = "fisheriescape:index"
    # grandparent_crumb = {"title": gettext_lazy("Analyses Search"), "url": reverse_lazy("fisheriescape:analyses_filter")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("fisheriescape:analyses_detail", kwargs=self.kwargs)}


#
# # ##########
# # # SCORES #
# # ##########
# #
#

class ScoreFilterView(FisheriescapeAccessRequired, CommonFilterView):
    template_name = "fisheriescape/score_filter.html"
    filterset_class = filters.ScoreFilter
    h1 = "Score Search"
    home_url_name = "fisheriescape:index"
    # row_object_url_name = "fisheriescape:fishery_detail"
    # new_btn_text = "New Analysis"

    queryset = models.Score.objects.annotate(
        search_term=Concat('species', 'id', output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'hexagon', "class": "", "width": ""},
        {"name": 'species', "class": "", "width": ""},
        {"name": 'week', "class": "", "width": ""},
        {"name": 'site_score', "class": "", "width": ""},
        {"name": 'ceu_score', "class": "", "width": ""},
        {"name": 'fs_score', "class": "", "width": ""},
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # contexts for scores maps
        hexagons = list(models.Score.objects.all()) + list(models.Hexagon.objects.all())
        # return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')

        # hexagons = models.Score.objects.all()

        context["hexagon_polygons"] = serialize("geojson", hexagons)
        context["mapbox_api_key"] = settings.MAPBOX_API_KEY

        return context

    # def get_new_object_url(self):
    #     return reverse("fisheriescape:analyses_new", kwargs=self.kwargs)


# class ScoreMapView(FisheriescapeAccessRequired, TemplateView):
#     template_name = "fisheriescape/search_map.html"
#
#     def get_context_data(self, **kwargs):
#         """Return the view context data."""
#         context = super().get_context_data(**kwargs)
#
#         hexagons = models.Hexagon.objects.filter(grid_id="BW-123")
#         context["hexagon_polygons"] = serialize("geojson", hexagons)
#         context["mapbox_api_key"] = settings.MAPBOX_API_KEY
#         return context


class ScoreMapView(FisheriescapeAccessRequired, CommonTemplateView):
    h1 = gettext_lazy("Test")
    template_name = "fisheriescape/search_map.html"
    field_list = [
        'id',
        'species',
        'week',
        'hexagon',
        'site_score',
        'ceu_score',
        'fs_score'
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["random_score"] = models.Score.objects.first()

        context["lobster_areas"] = serialize("geojson", models.FisheryArea.objects.filter(layer_id="Lobster"))
        context["snow_crab_areas"] = serialize("geojson", models.FisheryArea.objects.filter(layer_id="Crab"))
        context["herring_areas"] = serialize("geojson", models.FisheryArea.objects.filter(layer_id="Herring"))
        context["groundfish_areas"] = serialize("geojson", models.FisheryArea.objects.filter(layer_id="Groundfish"))
        context["nafo_sub_areas"] = serialize("geojson", models.FisheryArea.objects.filter(layer_id="NAFO Subareas"))
        context["nafo_areas"] = serialize("geojson", models.NAFOArea.objects.filter(layer_id="NAFO"))

        context["mapbox_api_key"] = settings.MAPBOX_API_KEY

        return context
