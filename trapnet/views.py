import json
import math

import numpy as np
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import TextField, Value
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext_lazy, gettext as _

from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from shared_models.models import River
from shared_models.views import CommonFormsetView, CommonHardDeleteView, CommonTemplateView, CommonFormView, CommonUpdateView, CommonCreateView, \
    CommonDeleteView, CommonDetailView, CommonFilterView, CommonPopoutCreateView, CommonPopoutUpdateView, CommonPopoutDeleteView
from . import filters
from . import forms
from . import models
from . import reports
from .mixins import TrapNetCRUDRequiredMixin, TrapNetAdminRequiredMixin, SuperuserOrAdminRequiredMixin, TrapNetBasicMixin
from .utils import get_sample_field_list, is_crud_user, get_age_from_length, get_sub_field_list


class IndexTemplateView(TrapNetBasicMixin, CommonTemplateView):
    template_name = 'trapnet/index.html'
    h1 = gettext_lazy("Home")


# Settings


class TrapNetUserFormsetView(SuperuserOrAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Trap Net Users"
    queryset = models.TrapNetUser.objects.all()
    formset_class = forms.TrapNetUserFormset
    success_url_name = "trapnet:manage_trap_net_users"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_trap_net_user"
    container_class = "container bg-light curvy"


class TrapNetUserHardDeleteView(SuperuserOrAdminRequiredMixin, CommonHardDeleteView):
    model = models.TrapNetUser
    success_url = reverse_lazy(":manage_trap_net_users")


class StatusFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Statuses"
    queryset = models.Status.objects.all()
    formset_class = forms.StatusFormset
    success_url_name = "trapnet:manage_statuses"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_status"


class StatusHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.Status
    success_url = reverse_lazy("trapnet:manage_statuses")


class SexFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Sexes"
    queryset = models.Sex.objects.all()
    formset_class = forms.SexFormset
    success_url_name = "trapnet:manage_sexes"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_sex"


class SexHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.Sex
    success_url = reverse_lazy("trapnet:manage_sexes")


class LifeStageFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Life Stages"
    queryset = models.LifeStage.objects.all()
    formset_class = forms.LifeStageFormset
    success_url_name = "trapnet:manage_life_stages"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_life_stage"


class LifeStageHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.LifeStage
    success_url = reverse_lazy("trapnet:manage_life_stages")


class OriginFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Origins"
    queryset = models.Origin.objects.all()
    formset_class = forms.OriginFormset
    success_url_name = "trapnet:manage_origins"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_origin"


class OriginHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.Origin
    success_url = reverse_lazy("trapnet:manage_origins")


class MaturityFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Maturities"
    queryset = models.Maturity.objects.all()
    formset_class = forms.MaturityFormset
    success_url_name = "trapnet:manage_maturities"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_maturity"


class MaturityHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.Maturity
    success_url = reverse_lazy("trapnet:manage_maturities")


class ElectrofisherFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Electrofishers"
    queryset = models.Electrofisher.objects.all()
    formset_class = forms.ElectrofisherFormset
    success_url_name = "trapnet:manage_electrofishers"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_electrofisher"


class ElectrofisherHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.Electrofisher
    success_url = reverse_lazy("trapnet:manage_electrofishers")


class ReproductiveStatusFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Reproductive Statuses"
    queryset = models.ReproductiveStatus.objects.all()
    formset_class = forms.ReproductiveStatusFormset
    success_url_name = "trapnet:manage_reproductive_statuses"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_reproductive_status"


class ReproductiveStatusHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.ReproductiveStatus
    success_url = reverse_lazy("trapnet:manage_reproductive_statuses")


class FishingAreaFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Fishing Areas"
    queryset = shared_models.FishingArea.objects.all()
    formset_class = forms.FishingAreaFormset
    success_url_name = "trapnet:manage_fishing_areas"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_fishing_area"


class FishingAreaHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = shared_models.FishingArea
    success_url = reverse_lazy("trapnet:manage_fishing_areas")


class MonitoringProgramFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Monitoring Programs"
    queryset = models.MonitoringProgram.objects.all()
    formset_class = forms.MonitoringProgramFormset
    success_url_name = "trapnet:manage_monitoring_programs"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_monitoring_program"


class MonitoringProgramHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.MonitoringProgram
    success_url = reverse_lazy("trapnet:manage_monitoring_programs")


# SPECIES #
###########

class SpeciesListView(TrapNetBasicMixin, CommonFilterView):
    template_name = "trapnet/list.html"
    filterset_class = filters.SpeciesFilter
    queryset = models.Species.objects.annotate(
        search_term=Concat('common_name_eng', Value(" "),
                           'common_name_fre', Value(" "),
                           'scientific_name', Value(" "),
                           'code', Value(" "),
                           'tsn', Value(" "),
                           output_field=TextField()))
    new_object_url_name = "trapnet:species_new"
    row_object_url_name = "trapnet:species_detail"
    home_url_name = "trapnet:index"
    paginate_by = 10

    field_list = [
        {"name": 'code', "class": "", "width": ""},
        {"name": 'full_name|{}'.format(_("Species")), "class": "", "width": ""},
        {"name": 'scientific_name', "class": "", "width": ""},
        {"name": 'tsn|{}'.format(_("Taxonomic serial number")), "class": "", "width": ""},
        {"name": 'aphia_id|{}'.format(_("WoRMS Aphia ID")), "class": "", "width": ""},
        # {"name": 'specimen_count|{}'.format(_("Specimens in Db")), "class": "", "width": ""},
    ]


class SpeciesCreateView(TrapNetAdminRequiredMixin, CommonCreateView):
    model = models.Species
    template_name = 'trapnet/form.html'
    form_class = forms.SpeciesForm
    home_url_name = "trapnet:index"
    parent_crumb = {"title": _("Species"), "url": reverse_lazy("trapnet:species_list")}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super().form_valid(form)


class SpeciesDetailView(TrapNetBasicMixin, CommonDetailView):
    model = models.Species
    template_name = "trapnet/species_detail.html"
    field_list = [
        'code',
        'common_name_eng',
        'common_name_fre',
        'abbrev',
        'scientific_name',
        'tsn',
        'aphia_id',
        'notes',
    ]
    home_url_name = "trapnet:index"
    parent_crumb = {"title": _("Species"), "url": reverse_lazy("trapnet:species_list")}


class SpeciesUpdateView(TrapNetAdminRequiredMixin, CommonUpdateView):
    model = models.Species
    template_name = 'trapnet/form.html'
    form_class = forms.SpeciesForm
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Species"), "url": reverse_lazy("trapnet:species_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:species_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class SpeciesDeleteView(TrapNetAdminRequiredMixin, CommonDeleteView):
    model = models.Species
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Species"), "url": reverse_lazy("trapnet:species_list")}

    def get_success_url(self):
        return self.get_grandparent_crumb()["url"]

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:species_detail", args=[self.get_object().id])}


# RIVER #
#########

class RiverListView(TrapNetBasicMixin, CommonFilterView):
    filterset_class = filters.RiverFilter
    template_name = 'trapnet/list.html'
    new_object_url_name = "trapnet:river_new"
    row_object_url_name = "trapnet:river_detail"
    home_url_name = "trapnet:index"
    queryset = River.objects.annotate(
        search_term=Concat('name', 'maritime_river_code', 'cgndb', output_field=TextField()))
    paginate_by = 25
    container_class = "container-fluid"
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'fishing_area', "class": "", "width": ""},
        {"name": 'maritime_river_code', "class": "", "width": ""},
        {"name": 'old_maritime_river_code', "class": "", "width": ""},
        {"name": 'cgndb', "class": "", "width": ""},
        {"name": 'parent_cgndb_id', "class": "", "width": ""},
        {"name": 'nbadw_water_body_id', "class": "", "width": ""},
        {"name": 'display_hierarchy|River hierarchy', "class": "", "width": ""},
        {"name": 'site_count|# sites', "class": "", "width": ""},
    ]


class RiverCreateView(TrapNetAdminRequiredMixin, CommonCreateView):
    model = shared_models.River
    form_class = forms.RiverForm
    template_name = 'trapnet/form.html'
    home_url_name = "trapnet:index"
    parent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super().form_valid(form)


class RiverDetailView(TrapNetBasicMixin, CommonDetailView):
    model = shared_models.River
    template_name = 'trapnet/river_detail.html'
    field_list = [
        'name',
        'fishing_area_code',
        'maritime_river_code',
        'old_maritime_river_code',
        'cgndb',
        'parent_cgndb_id',
        'nbadw_water_body_id',
        'display_anchored_hierarchy|River hierarchy',
        'metadata',
    ]
    home_url_name = "trapnet:index"
    parent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_field_list'] = [
            'name',
            'stream_order',
            'elevation_m',
            'province.abbrev_eng',
            'latitude',
            'longitude',
            'directions',
            'notes',
        ]
        context['my_site_object'] = models.RiverSite.objects.first()
        return context


class RiverUpdateView(TrapNetAdminRequiredMixin, CommonUpdateView):
    model = shared_models.River
    form_class = forms.RiverForm
    template_name = 'trapnet/form.html'
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:river_detail", args=[self.get_object().id])}


class RiverDeleteView(TrapNetAdminRequiredMixin, CommonDeleteView):
    model = shared_models.River
    success_url = reverse_lazy('trapnet:river_list')
    template_name = 'trapnet/confirm_delete.html'
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:river_detail", args=[self.get_object().id])}


# SITE #
########

class RiverSiteCreateView(TrapNetAdminRequiredMixin, CommonCreateView):
    model = models.RiverSite
    template_name = 'trapnet/form.html'
    form_class = forms.RiverSiteForm
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def get_parent_crumb(self):
        return {"title": self.get_river(), "url": reverse("trapnet:river_detail", args=[self.get_river().id])}

    def get_river(self):
        return get_object_or_404(River, pk=self.kwargs.get("river"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['river'] = self.get_river()
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.river = self.get_river()
        obj.created_by = self.request.user
        return super().form_valid(form)


class RiverSiteUpdateView(TrapNetAdminRequiredMixin, CommonUpdateView):
    model = models.RiverSite
    template_name = 'trapnet/form.html'
    form_class = forms.RiverSiteForm
    home_url_name = "trapnet:index"
    greatgrandparent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().river, "url": reverse("trapnet:river_detail", args=[self.get_object().river.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:site_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class RiverSiteDetailView(TrapNetBasicMixin, CommonDetailView):
    model = models.RiverSite
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}
    field_list = [
        'name',
        'river',
        'stream_order',
        'elevation_m',
        'province.abbrev_eng',
        'coordinates',
        'epsg_id',
        'directions',
        'notes',
        'metadata',
    ]

    def get_parent_crumb(self):
        return {"title": self.get_object().river, "url": reverse("trapnet:river_detail", args=[self.get_object().river.id])}


class RiverSiteDeleteView(TrapNetAdminRequiredMixin, CommonDeleteView):
    model = models.RiverSite
    home_url_name = "trapnet:index"
    greatgrandparent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().river, "url": reverse("trapnet:river_detail", args=[self.get_object().river.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:site_detail", args=[self.get_object().id])}

    def get_success_url(self):
        return self.get_grandparent_crumb()["url"]


# SAMPLE #
##########

class SampleListView(TrapNetBasicMixin, CommonFilterView):
    model = models.Sample
    filterset_class = filters.SampleFilter
    template_name = 'trapnet/sample_list.html'
    queryset = models.Sample.objects.all()
    new_object_url_name = "trapnet:sample_new"
    row_object_url_name = "trapnet:sample_detail"
    home_url_name = "trapnet:index"
    paginate_by = 25
    container_class = "container"
    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'season', "class": "", "width": ""},
        {"name": 'sample_type', "class": "", "width": ""},
        {"name": 'site', "class": "", "width": ""},
        {"name": 'arrival_date|arrival', "class": "", "width": ""},
        {"name": 'duration|duration', "class": "", "width": ""},
        {"name": 'specimens', "class": "", "width": ""},
        {"name": 'is_reviewed', "class": "", "width": ""},
    ]


class SampleUpdateView(TrapNetCRUDRequiredMixin, CommonUpdateView):
    model = models.Sample
    form_class = forms.SampleForm
    template_name = 'trapnet/sample_form/basic.html'
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}

    def get_template_names(self):
        obj = self.get_object()
        if obj.sample_type == 1:
            return 'trapnet/sample_form/rst.html'
        elif obj.sample_type == 2:
            return 'trapnet/sample_form/ef.html'
        elif obj.sample_type == 3:
            return 'trapnet/sample_form/trapnet.html'
        else:
            return self.template_name

    def get_sub_form_class(self):
        obj = self.get_object()
        form = None
        if obj.sample_type == 1:
            form = forms.RSTSampleForm
        elif obj.sample_type == 2:
            form = forms.EFSampleForm
        elif obj.sample_type == 3:
            form = forms.TrapnetSampleForm
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["sub_form"] = self.get_sub_form_class()(instance=obj.get_sub_obj())
        return context

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:sample_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        sub_obj = obj.get_sub_obj()

        sub_data = dict()
        sub_fields = [f.name for f in sub_obj._meta.fields]
        for key in self.request.POST:
            if key in sub_fields:
                sub_data[key] = self.request.POST[key]
        sub_form = self.get_sub_form_class()(data=sub_data, instance=sub_obj)

        if not sub_form.is_valid():
            context = self.get_context_data(form=form)
            context["sub_form"] = sub_form
            return self.render_to_response(context)

        sub_form.save()

        return super().form_valid(form)

    def get_initial(self):
        obj = self.get_object()
        if obj.percent_cloud_cover:
            return dict(percent_cloud_cover=obj.percent_cloud_cover * 100)


class SampleCreateView(TrapNetCRUDRequiredMixin, CommonCreateView):
    model = models.Sample
    form_class = forms.SampleForm
    template_name = 'trapnet/sample_form/basic.html'
    home_url_name = "trapnet:index"
    parent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        super().form_valid(form)
        if form.cleaned_data.get("stay_on_page"):
            return HttpResponseRedirect(reverse_lazy("trapnet:sample_edit", args=[obj.id]))
        return super().form_valid(form)


class SampleDetailView(TrapNetBasicMixin, CommonDetailView):
    model = models.Sample
    template_name = 'trapnet/sample_detail/basic.html'
    home_url_name = "trapnet:index"
    parent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = super().get_context_data(**kwargs)
        context['basic_field_list'] = get_sample_field_list()
        context['sub_field_list'] = get_sub_field_list(obj)
        context["sub_obj"] = obj.get_sub_obj()
        context["sub_title"] = obj.get_sub_obj()
        context['specimen_field_list'] = [
            'species',
            'status',
            'fork_length',
            'weight',
            'tag_number',
            "smart_river_age|{}".format("smart river age"),
            # 'age_type',
            'scale_id_number',
            'notes',
        ]

        context['historical_file_field_list'] = [
            "species",
            "maturity",
            "status",
            "sex",
            "life_stage",
            "fork_length",
            "total_length",
            "weight",
            "age_type",
            "river_age",
            "old_id",
        ]

        context['sweep_field_list'] = [
            "sweep_number",
            "sweep_time",
            "specimen_count|{}".format("# specimens"),
        ]
        salmon_with_lengths = obj.get_salmon_with_lengths()
        if salmon_with_lengths.exists():
            hist = dict(data=list(), colors=list(), max_count=0)
            lengths = [item.fork_length for item in salmon_with_lengths]

            # get the data for the histogram
            len_range = range(math.floor(min(lengths)), math.ceil(max(lengths)))
            counts, bins = np.histogram(lengths, bins=math.ceil(len(len_range) * 0.5))
            hist_zip = zip(bins, counts)

            for item in hist_zip:
                length = item[0]
                count = item[1]
                hist["data"].append(dict(x=length, y=count))
                age = get_age_from_length(length, obj.age_thresh_0_1, obj.age_thresh_1_2)
                if age == 0:  # green
                    hist["colors"].append('rgba(75, 192, 192, 0.5)')
                elif age == 1:  # purple
                    hist["colors"].append('rgba(153, 102, 255, 0.5)')
                elif age == 2:  # red
                    hist["colors"].append('rgba(255, 99, 132, 0.5)')
                else:  # grey
                    hist["colors"].append('rgba(16,16,16,0.5)')
                if count > hist["max_count"]:
                    hist["max_count"] = count
            context['hist'] = hist

        detailed_salmon = obj.get_detailed_salmon()
        if detailed_salmon.exists():
            lw = dict(obs_data=list(), exp_data=list(), colors=list())
            obs_data = [dict(x=s.fork_length, y=s.weight) for s in detailed_salmon]
            lw['obs_data'] = obs_data
            lengths = [item["x"] for item in obs_data]
            weights = [item["y"] for item in obs_data]
            for length in lengths:
                age = get_age_from_length(length, obj.age_thresh_0_1, obj.age_thresh_1_2)
                if age == 0:  # green
                    lw["colors"].append('rgba(75, 192, 192, 0.5)')
                elif age == 1:  # purple
                    lw["colors"].append('rgba(153, 102, 255, 0.5)')
                elif age == 2:  # red
                    lw["colors"].append('rgba(255, 99, 132, 0.5)')
                else:  # grey
                    lw["colors"].append('rgba(16,16,16,0.5)')

            len_range = range(math.floor(min(lengths)), math.ceil(max(lengths)))
            calc_pairs = list()
            for l in len_range:
                a = 0.00561
                b = 3.125999999999999
                wgt = (a * l ** b) / 1000
                lw["exp_data"].append(dict(x=l, y=wgt))
            context['lw'] = json.dumps(lw)

            # get the data for the histogram
            counts, bins = np.histogram(lengths, bins=math.ceil(len(len_range) * 0.5))
            hist_zip = zip(bins, counts)
            hist_data = list()
            hist_colors = list()
            hist_labels = list()
            for item in hist_zip:
                hist_data.append(dict(x=item[0], y=item[1], color="red"))
                age = get_age_from_length(item[0], obj.age_thresh_0_1, obj.age_thresh_1_2)
                if age == 0:  # green
                    hist_colors.append('rgba(75, 192, 192, 0.5)')
                elif age == 1:  # purple
                    hist_colors.append('rgba(153, 102, 255, 0.5)')
                elif age == 2:  # red
                    hist_colors.append('rgba(255, 99, 132, 0.5)')
                else:  # grey
                    hist_colors.append('rgba(16,16,16,0.5)')
                hist_labels.append('age not assigned')

            context['hist_data'] = hist_data
            context['hist_colors'] = hist_colors
            context['hist_labels'] = hist_labels
            context['hist_max_count'] = max(counts)
            context['max_weight'] = max(weights)

        return context


class SampleDeleteView(TrapNetAdminRequiredMixin, CommonDeleteView):
    model = models.Sample
    template_name = 'trapnet/confirm_delete.html'
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}
    delete_protection = False

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:sample_detail", args=[self.get_object().id])}

    def get_success_url(self):
        return self.get_grandparent_crumb()["url"]


@login_required(login_url='/accounts/login/')
@user_passes_test(is_crud_user, login_url='/accounts/denied/?app=trapnet')
def review_sample(request, pk):
    obj = get_object_or_404(models.Sample, pk=pk)
    if obj.is_reviewed:
        obj.is_reviewed = False
        obj.reviewed_by = None
        obj.reviewed_at = None
    else:
        obj.is_reviewed = True
        obj.reviewed_by = request.user
        obj.reviewed_at = timezone.now()
    obj.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class DataEntryVueJSView(TrapNetCRUDRequiredMixin, CommonTemplateView):
    template_name = 'trapnet/data_entry_v2/main.html'
    home_url_name = "trapnet:index"
    greatgrandparent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}
    container_class = "container-fluid"
    active_page_name_crumb = gettext_lazy("Data Entry Mode")
    h1 = " "

    def get_grandparent_crumb(self):
        if self.kwargs.get("sweep"):
            sweep = get_object_or_404(models.Sweep, pk=self.kwargs.get("sweep"))
            return {"title": sweep.sample, "url": reverse("trapnet:sample_detail", args=[sweep.sample.id])}
        elif self.kwargs.get("sample"):
            sample = get_object_or_404(models.Sample, pk=self.kwargs.get("sample"))
            return {"title": sample, "url": reverse("trapnet:sample_detail", args=[sample.id])}

    def get_parent_crumb(self):
        if self.kwargs.get("sweep"):
            sweep = get_object_or_404(models.Sweep, pk=self.kwargs.get("sweep"))
            return {"title": sweep, "url": reverse("trapnet:sweep_detail", args=[sweep.id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sample_id = self.kwargs.get("sample")
        sweep_id = self.kwargs.get("sweep")
        if not sample_id:
            sample_id = get_object_or_404(models.Sweep, pk=sweep_id).sample_id

        context["sample_id"] = nz(sample_id, "null")
        context["sweep_id"] = nz(sweep_id, "null")

        return context


# SWEEPS #
##########

class SweepCreateView(TrapNetCRUDRequiredMixin, CommonCreateView):
    model = models.Sweep
    template_name = 'trapnet/form.html'
    form_class = forms.SweepForm
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}

    def get_initial(self):
        sample = self.get_sample()
        if not sample.sweeps.exists():
            return dict(sweep_number=0.5)
        else:
            last = sample.sweeps.order_by("sweep_number").last().sweep_number
            next_number = 1 if last == 0.5 else last + 1
            return dict(sweep_number=next_number)

    def get_parent_crumb(self):
        return {"title": self.get_sample(), "url": reverse("trapnet:sample_detail", args=[self.get_sample().id])}

    def get_sample(self):
        return get_object_or_404(models.Sample, pk=self.kwargs.get("sample"))

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.sample = self.get_sample()
        obj.created_by = self.request.user
        return super().form_valid(form)


class SweepUpdateView(TrapNetCRUDRequiredMixin, CommonUpdateView):
    model = models.Sweep
    form_class = forms.SweepForm
    template_name = 'trapnet/form.html'
    home_url_name = "trapnet:index"
    greatgrandparent_crumb = {"title": _("Sweeps"), "url": reverse_lazy("trapnet:sample_list")}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().sample, "url": reverse("trapnet:sample_detail", args=[self.get_object().sample.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:sweep_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class SweepDetailView(TrapNetBasicMixin, CommonDetailView):
    model = models.Sweep
    template_name = 'trapnet/sweep_detail.html'
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}
    field_list = [
        'sweep_number',
        'sweep_time',
        'species_list|{}'.format(_("species caught")),
        'tag_list|{}'.format(_("tags issued")),
        'notes',
        'metadata',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specimen_field_list'] = [
            'species',
            'status',
            'adipose_condition',
            'sex',
            'scale_id_number',
        ]
        return context

    def get_parent_crumb(self):
        return {"title": self.get_object().sample, "url": reverse("trapnet:sample_detail", args=[self.get_object().sample.id])}


class SweepDeleteView(TrapNetCRUDRequiredMixin, CommonDeleteView):
    model = models.Sweep
    template_name = 'trapnet/confirm_delete.html'
    home_url_name = "trapnet:index"
    greatgrandparent_crumb = {"title": _("Sweeps"), "url": reverse_lazy("trapnet:sample_list")}
    delete_protection = False

    def get_grandparent_crumb(self):
        return {"title": self.get_object().sample, "url": reverse("trapnet:sample_detail", args=[self.get_object().sample.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:sweep_detail", args=[self.get_object().id])}

    def get_success_url(self):
        return self.get_grandparent_crumb()["url"]


# OBSERVATIONS #
################


class SpecimenListView(TrapNetBasicMixin, CommonFilterView):
    model = models.Specimen
    filterset_class = filters.SpecimenFilter
    template_name = 'trapnet/specimen_list.html'
    # open_row_in_new_tab = True
    # row_object_url_name = "trapnet:specimen_detail"
    home_url_name = "trapnet:index"
    paginate_by = 25
    container_class = "container"
    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'sample', "class": "", "width": ""},
        {"name": 'sample.site|{}'.format(_("site")), "class": "", "width": ""},
        {"name": 'species', "class": "", "width": ""},
        {"name": 'status', "class": "", "width": ""},
        {"name": 'sex', "class": "", "width": ""},
        {"name": 'tag_number', "class": "", "width": ""},
        {"name": 'scale_id_number', "class": "", "width": ""},
    ]


class SpecimenUpdateView(TrapNetCRUDRequiredMixin, CommonUpdateView):
    model = models.Specimen
    form_class = forms.SpecimenForm
    template_name = 'trapnet/form.html'
    home_url_name = "trapnet:index"

    def get_greatgrandparent_crumb(self):
        if self.get_object().sweep:
            sweep = self.get_object().sweep
            return {"title": sweep.sample, "url": reverse("trapnet:sample_detail", args=[sweep.sample.id])}
        else:
            sample = self.get_object().sample
            return {"title": sample, "url": reverse("trapnet:sample_detail", args=[sample.id])}

    def get_grandparent_crumb(self):
        if self.get_object().sweep:
            sweep = self.get_object().sweep
            return {"title": sweep, "url": reverse("trapnet:sweep_detail", args=[sweep.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:specimen_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class SpecimenDetailView(TrapNetBasicMixin, CommonDetailView):
    model = models.Specimen
    template_name = 'trapnet/specimen_detail.html'
    home_url_name = "trapnet:index"
    field_list = [
        'id',
        'species',
        'life_stage',
        'reproductive_status',
        'status',
        'adipose_condition',
        'sex',
        'fork_length',
        'total_length',
        'weight',
        'age_type',
        'river_age',
        'ocean_age',
        'tag_number',
        'scale_id_number',
        'notes',
        'metadata',
    ]
    greatgrandparent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}

    def get_grandparent_crumb(self):
        if self.get_object().sweep:
            sweep = self.get_object().sweep
            return {"title": sweep.sample, "url": reverse("trapnet:sample_detail", args=[sweep.sample.id])}
        else:
            sample = self.get_object().sample
            return {"title": sample, "url": reverse("trapnet:sample_detail", args=[sample.id])}

    def get_parent_crumb(self):
        if self.get_object().sweep:
            sweep = self.get_object().sweep
            return {"title": sweep, "url": reverse("trapnet:sweep_detail", args=[sweep.id])}


class SpecimenDeleteView(TrapNetCRUDRequiredMixin, CommonDeleteView):
    model = models.Specimen
    template_name = 'trapnet/confirm_delete.html'
    home_url_name = "trapnet:index"

    def get_greatgrandparent_crumb(self):
        if self.get_object().sweep:
            sweep = self.get_object().sweep
            return {"title": sweep.sample, "url": reverse("trapnet:sample_detail", args=[sweep.sample.id])}
        else:
            sample = self.get_object().sample
            return {"title": sample, "url": reverse("trapnet:sample_detail", args=[sample.id])}

    def get_grandparent_crumb(self):
        if self.get_object().sweep:
            sweep = self.get_object().sweep
            return {"title": sweep, "url": reverse("trapnet:sweep_detail", args=[sweep.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:specimen_detail", args=[self.get_object().id])}

    def get_success_url(self):
        return self.get_grandparent_crumb()["url"]


# FILES #
#########

class FileCreateView(TrapNetCRUDRequiredMixin, CommonPopoutCreateView):
    model = models.File
    form_class = forms.FileForm
    is_multipart_form_data = True

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        specimen = get_object_or_404(models.Specimen, pk=self.kwargs.get("specimen"))
        obj.specimen = specimen
        return super().form_valid(form)


class FileUpdateView(TrapNetCRUDRequiredMixin, CommonPopoutUpdateView):
    model = models.File
    form_class = forms.FileForm
    is_multipart_form_data = True

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class FileDeleteView(TrapNetCRUDRequiredMixin, CommonPopoutDeleteView):
    model = models.File


# SAMPLE FILES #
################

class SampleFileCreateView(TrapNetCRUDRequiredMixin, CommonPopoutCreateView):
    model = models.SampleFile
    form_class = forms.SampleFileForm
    is_multipart_form_data = True

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.sample = get_object_or_404(models.Sample, pk=self.kwargs.get("sample"))
        return super().form_valid(form)


class SampleFileUpdateView(TrapNetCRUDRequiredMixin, CommonPopoutUpdateView):
    model = models.SampleFile
    form_class = forms.SampleFileForm
    is_multipart_form_data = True

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class SampleFileDeleteView(TrapNetCRUDRequiredMixin, CommonPopoutDeleteView):
    model = models.SampleFile


# REPORTS #
###########

class ReportSearchFormView(TrapNetCRUDRequiredMixin, CommonFormView):
    template_name = 'trapnet/report_search.html'
    form_class = forms.ReportSearchForm
    h1 = " "

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        # ais_species_list = str(form.cleaned_data["ais_species"]).replace("[", "").replace("]", "").replace(" ", "").replace("'","").replace('"',"")

        report = int(form.cleaned_data["report"])
        year = form.cleaned_data["year"] if form.cleaned_data["year"] else ""
        sample_type = form.cleaned_data["sample_type"] if form.cleaned_data["sample_type"] else ""
        fishing_areas = listrify(form.cleaned_data["fishing_areas"]) if len(form.cleaned_data["fishing_areas"]) > 0 else ""
        rivers = listrify(form.cleaned_data["rivers"]) if len(form.cleaned_data["rivers"]) > 0 else ""
        sites = listrify(form.cleaned_data["sites"]) if len(form.cleaned_data["sites"]) > 0 else ""

        # raw reports
        if report == 1:
            return HttpResponseRedirect(
                reverse("trapnet:sample_report") + f"?sample_type={sample_type}&year={year}&fishing_areas={fishing_areas}&rivers={rivers}&sites={sites}")
        elif report == 2:
            return HttpResponseRedirect(reverse("trapnet:sweep_report") + f"?year={year}&fishing_areas={fishing_areas}&rivers={rivers}&sites={sites}")
        elif report == 3:
            return HttpResponseRedirect(
                reverse("trapnet:specimen_report") + f"?year={year}&fishing_areas={fishing_areas}&rivers={rivers}&sites={sites}&sample_type={sample_type}")
        elif report == 5:
            return HttpResponseRedirect(reverse(
                "trapnet:biological_detailing_report") + f"?year={year}&fishing_areas={fishing_areas}&rivers={rivers}&sites={sites}&sample_type={sample_type}")

        # custom - other
        elif report == 4:
            return HttpResponseRedirect(reverse(
                "trapnet:export_specimen_data_v1") + f"?year={year}&fishing_areas={fishing_areas}&rivers={rivers}&sites={sites}&sample_type={sample_type}")

        # custom - electrofishing
        elif report == 10:
            return HttpResponseRedirect(reverse("trapnet:electro_juv_salmon_report") + f"?year={year}&fishing_areas={fishing_areas}&rivers={rivers}")

        # Open data
        elif report == 91:
            return HttpResponseRedirect(reverse("trapnet:od1_report", kwargs={"year": year, "sites": sites}))
        elif report == 92:
            return HttpResponseRedirect(reverse("trapnet:od1_dictionary"))
        elif report == 93:
            return HttpResponseRedirect(reverse("trapnet:od_spp_list"))
        elif report == 94:
            return HttpResponseRedirect(reverse("trapnet:od1_wms", kwargs={"lang": 1}))
        elif report == 95:
            return HttpResponseRedirect(reverse("trapnet:od1_wms", kwargs={"lang": 2}))
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("trapnet:reports"))


def export_sample_data(request):
    sample_type = request.GET.get("sample_type")
    year = request.GET.get("year")
    fishing_areas = request.GET.get("fishing_areas")
    rivers = request.GET.get("rivers")
    sites = request.GET.get("sites")

    filename_prefix = ""
    filter_kwargs = {}
    if year != "":
        filter_kwargs["season"] = year
    if sample_type != "":
        filter_kwargs["sample_type"] = sample_type
        if sample_type == "1":
            filename_prefix = "RST "
        elif sample_type == "2":
            filename_prefix = "EF "
        elif sample_type == "3":
            filename_prefix = "trapnet "
    if fishing_areas != "":
        filter_kwargs["site__river__fishing_area_id__in"] = fishing_areas.split(",")
    if rivers != "":
        filter_kwargs["site__river_id__in"] = rivers.split(",")
    if sites != "":
        filter_kwargs["site_id__in"] = sites.split(",")

    qs = models.Sample.objects.filter(**filter_kwargs)
    filename = f"{filename_prefix}sample data ({now().strftime('%Y-%m-%d')}).csv"

    response = StreamingHttpResponse(
        streaming_content=(reports.generate_sample_csv(qs)),
        content_type='text/csv',
    )
    response['Content-Disposition'] = f'attachment;filename={filename}'
    return response


def export_sweep_data(request):
    year = request.GET.get("year")
    fishing_areas = request.GET.get("fishing_areas")
    rivers = request.GET.get("rivers")
    sites = request.GET.get("sites")

    filter_kwargs = {}
    if year != "":
        filter_kwargs["sample__season"] = year
    if fishing_areas != "":
        filter_kwargs["sample__site__river__fishing_area_id__in"] = fishing_areas.split(",")
    if rivers != "":
        filter_kwargs["sample__site__river_id__in"] = rivers.split(",")
    if sites != "":
        filter_kwargs["sample__site_id__in"] = sites.split(",")

    qs = models.Sweep.objects.filter(**filter_kwargs)
    filename = "EF sweep data ({}).csv".format(now().strftime("%Y-%m-%d"))

    response = StreamingHttpResponse(
        streaming_content=(reports.generate_sweep_csv(qs)),
        content_type='text/csv',
    )
    response['Content-Disposition'] = f'attachment;filename={filename}'
    return response


def export_specimen_data(request):
    sample_type = request.GET.get("sample_type")
    year = request.GET.get("year")
    fishing_areas = request.GET.get("fishing_areas")
    rivers = request.GET.get("rivers")
    sites = request.GET.get("sites")

    filename_prefix = ""
    filter_kwargs = {}
    if year != "":
        filter_kwargs["sample__season"] = year
    if sample_type != "":
        filter_kwargs["sample__sample_type"] = sample_type
        if sample_type == "1":
            filename_prefix = "RST "
        elif sample_type == "2":
            filename_prefix = "EF "
        elif sample_type == "3":
            filename_prefix = "trapnet "
    if fishing_areas != "":
        filter_kwargs["sample__site__river__fishing_area_id__in"] = fishing_areas.split(",")
    if rivers != "":
        filter_kwargs["sample__site__river_id__in"] = rivers.split(",")
    if sites != "":
        filter_kwargs["sample__site_id__in"] = sites.split(",")

    qs = models.Specimen.objects.filter(**filter_kwargs).iterator()
    filename = f"{filename_prefix}specimen data ({now().strftime('%Y-%m-%d')}).csv"

    response = StreamingHttpResponse(
        streaming_content=(reports.generate_specimen_csv(qs, int(sample_type))),
        content_type='text/csv',
    )
    response['Content-Disposition'] = f'attachment;filename={filename}'
    return response


def export_biological_detailing_data(request):
    sample_type = request.GET.get("sample_type")
    year = request.GET.get("year")
    fishing_areas = request.GET.get("fishing_areas")
    rivers = request.GET.get("rivers")
    sites = request.GET.get("sites")

    filter_kwargs = {}
    if year != "":
        filter_kwargs["sample__season"] = year
    if sample_type != "":
        filter_kwargs["sample__sample_type"] = sample_type
    if fishing_areas != "":
        filter_kwargs["sample__site__river__fishing_area_id__in"] = fishing_areas.split(",")
    if rivers != "":
        filter_kwargs["sample__site__river_id__in"] = rivers.split(",")
    if sites != "":
        filter_kwargs["sample__site_id__in"] = sites.split(",")

    qs = models.BiologicalDetailing.objects.filter(**filter_kwargs).iterator()
    filename = f"historical biological data ({now().strftime('%Y-%m-%d')}).csv"

    response = StreamingHttpResponse(
        streaming_content=(reports.generate_biological_detailing_csv(qs)),
        content_type='text/csv',
    )
    response['Content-Disposition'] = f'attachment;filename={filename}'
    return response


def export_specimen_data_v1(request):
    year = request.GET.get("year")
    fishing_areas = request.GET.get("fishing_areas")
    sample_type = request.GET.get("sample_type")
    rivers = request.GET.get("rivers")
    sites = request.GET.get("sites")

    filter_kwargs = {"species__scientific_name__istartswith": "salmo", "life_stage__name__iexact": "smolt"}
    if year != "":
        filter_kwargs["sample__season"] = year
    if fishing_areas != "":
        filter_kwargs["sample__site__river__fishing_area_id__in"] = fishing_areas.split(",")
    if sample_type != "":
        filter_kwargs["sample__sample_type"] = sample_type
    if rivers != "":
        filter_kwargs["sample__site__river_id__in"] = rivers.split(",")
    if sites != "":
        filter_kwargs["sample__site_id__in"] = sites.split(",")
    qs = models.Specimen.objects.filter(**filter_kwargs).iterator()

    filename = "Atlantic salmon individual specimen event report ({}).csv".format(now().strftime("%Y-%m-%d"))
    response = StreamingHttpResponse(
        streaming_content=(reports.generate_specimen_csv_v1(qs)),
        content_type='text/csv',
    )
    response['Content-Disposition'] = f'attachment;filename={filename}'
    return response


def electro_juv_salmon_report(request):
    year = request.GET.get("year")
    fishing_areas = request.GET.get("fishing_areas")
    rivers = request.GET.get("rivers")

    filter_kwargs = {
        "sample__sample_type": 2
    }
    if year != "":
        filter_kwargs["sample__season"] = year
    if fishing_areas != "":
        filter_kwargs["sample__site__river__fishing_area_id__in"] = fishing_areas.split(",")
    if rivers != "":
        filter_kwargs["sample__site__river_id__in"] = rivers.split(",")

    qs = models.Sweep.objects.filter(**filter_kwargs)

    filename = "juv_salmon_csas_report.csv"
    response = StreamingHttpResponse(
        streaming_content=(reports.generate_electro_juv_salmon_report(qs)),
        content_type='text/csv',
    )
    response['Content-Disposition'] = f'attachment;filename={filename}'
    return response


def export_open_data_ver1(request, year, sites):
    response = reports.generate_open_data_ver_1_report(year, sites)
    return response


def export_open_data_ver1_dictionary(request):
    response = reports.generate_open_data_ver_1_data_dictionary()
    return response


def export_spp_list(request):
    response = reports.generate_spp_list()
    return response


def export_open_data_ver1_wms(request, lang):
    response = reports.generate_open_data_ver_1_wms_report(lang)
    return response


###########

class BiologicalDetailingListView(TrapNetBasicMixin, CommonFilterView):
    template_name = 'trapnet/list.html'
    model = models.BiologicalDetailing
    filterset_class = filters.BiologicalDetailingFilter
    home_url_name = "trapnet:index"
    row_object_url_name = "trapnet:biological_detailing_detail"
    container_class = "container-fluid"
    paginate_by = 10
    fields = [
        "sample",
        "old_id",
        "species",
        "reproductive_status",
        "maturity",
        "status",
        "sex",
        "adipose_condition",
        "life_stage",
        "fork_length",
        "total_length",
        "weight",
        "age_type",
        "river_age",
        "notes",
    ]


class BiologicalDetailingDetailView(TrapNetBasicMixin, CommonDetailView):
    model = models.BiologicalDetailing
    template_name = 'trapnet/detail.html'
    # edit_url_name = "trapnet:biological_detailing_edit"
    # delete_url_name = "trapnet:biological_detailing_delete"
    home_url_name = "trapnet:index"
    parent_crumb = {"title": gettext_lazy("Biological Detailings"), "url": reverse_lazy("trapnet:biological_detailing_list")}
    container_class = "container"

# class BiologicalDetailingUpdateView(TrapNetCRUDRequiredMixin, CommonUpdateView):
#     model = models.BiologicalDetailing
#     form_class = forms.BiologicalDetailingForm
#     template_name = 'trapnet/form.html'
#     home_url_name = "trapnet:index"
#     grandparent_crumb = {"title": gettext_lazy("Biological Detailings"), "url": reverse_lazy("trapnet:biological_detailing_list")}
#     container_class = "container"
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object(), "url": reverse("trapnet:biological_detailing_detail", args=[self.get_object().id])}
#
#
# class BiologicalDetailingDeleteView(TrapNetCRUDRequiredMixin, CommonDeleteView):
#     model = models.BiologicalDetailing
#     success_url = reverse_lazy('trapnet:biological_detailing_list')
#     success_message = 'The Biological Detailing was successfully deleted!'
#     template_name = 'trapnet/confirm_delete.html'
#     container_class = "container"
#     delete_protection = False
#     home_url_name = "trapnet:index"
#     grandparent_crumb = {"title": gettext_lazy("Biological Detailings"), "url": reverse_lazy("trapnet:biological_detailing_list")}
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object(), "url": reverse("trapnet:biological_detailing_detail", args=[self.get_object().id])}
