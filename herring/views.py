import collections
import csv
import math
from datetime import datetime
from io import StringIO

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db.models import Q, TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView, ListView
from django_filters.views import FilterView, FilterMixin
from numpy import arange

from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from shared_models.models import Port
from shared_models.views import CommonFormsetView, CommonHardDeleteView, CommonListView, CommonTemplateView, CommonFilterView, CommonDetailView, CommonFormView, \
    CommonCreateView, CommonDeleteView, CommonUpdateView
from . import filters
from . import forms
from . import models
from . import reports
from .mixins import SuperuserOrAdminRequiredMixin, HerringBasicMixin, HerringAdmin, HerringCRUD, HerringAccess


class HerringUserFormsetView(SuperuserOrAdminRequiredMixin, CommonFormsetView):
    template_name = 'herring/formset.html'
    h1 = "Manage Herring Users"
    queryset = models.HerringUser.objects.all()
    formset_class = forms.HerringUserFormset
    success_url_name = "herring:manage_herring_users"
    home_url_name = "herring:index"
    delete_url_name = "herring:delete_herring_user"
    container_class = "container bg-light curvy"


class HerringUserHardDeleteView(SuperuserOrAdminRequiredMixin, CommonHardDeleteView):
    model = models.HerringUser
    success_url = reverse_lazy("herring:manage_herring_users")


class IndexView(HerringBasicMixin, CommonTemplateView):
    template_name = 'herring/index.html'
    h1 = "Home"


# Settings #
###########


class SamplerFormsetView(HerringAdmin, CommonFormsetView):
    template_name = 'herring/formset.html'
    h1 = "Manage Samplers"
    queryset = models.Sampler.objects.all()
    formset_class = forms.SamplerFormset
    success_url_name = "herring:manage_samplers"
    home_url_name = "herring:index"
    delete_url_name = "herring:delete_sampler"
    post_display_fields = ["sample_count|Number of samples collected"]


class SamplerHardDeleteView(HerringAdmin, CommonHardDeleteView):
    model = models.Sampler
    success_url = reverse_lazy("herring:manage_samplers")


class GearFormsetView(HerringAdmin, CommonFormsetView):
    template_name = 'herring/formset.html'
    h1 = "Manage Gear Types"
    queryset = models.Gear.objects.all()
    formset_class = forms.GearFormset
    success_url_name = "herring:manage_gears"
    home_url_name = "herring:index"
    delete_url_name = "herring:delete_gear"


class GearHardDeleteView(HerringAdmin, CommonHardDeleteView):
    model = models.Gear
    success_url = reverse_lazy("herring:manage_gears")


class FishingAreaFormsetView(HerringAdmin, CommonFormsetView):
    template_name = 'herring/formset.html'
    h1 = "Manage Fishing Areas"
    queryset = models.FishingArea.objects.all()
    formset_class = forms.FishingAreaFormset
    success_url_name = "herring:manage_fishing_areas"
    home_url_name = "herring:index"
    delete_url_name = "herring:delete_fishing_area"


class FishingAreaHardDeleteView(HerringAdmin, CommonHardDeleteView):
    model = models.FishingArea
    success_url = reverse_lazy("herring:manage_fishing_areas")


class MeshSizeFormsetView(HerringAdmin, CommonFormsetView):
    template_name = 'herring/formset.html'
    h1 = "Manage Mesh Sizes"
    queryset = models.MeshSize.objects.all()
    formset_class = forms.MeshSizeFormset
    success_url_name = "herring:manage_mesh_sizes"
    home_url_name = "herring:index"
    delete_url_name = "herring:delete_mesh_size"


class MeshSizeHardDeleteView(HerringAdmin, CommonHardDeleteView):
    model = models.MeshSize
    success_url = reverse_lazy("herring:manage_mesh_sizes")


class PortFormsetView(HerringAdmin, CommonFormsetView):
    template_name = 'herring/formset.html'
    h1 = "Manage Ports"
    queryset = Port.objects.all()
    formset_class = forms.PortFormset
    success_url_name = "herring:manage_ports"
    home_url_name = "herring:index"
    delete_url_name = "herring:delete_port"


class PortHardDeleteView(HerringAdmin, CommonHardDeleteView):
    model = Port
    success_url = reverse_lazy("herring:manage_ports")


# SAMPLE #
##########
class SampleFilterView(HerringAccess, CommonFilterView):
    home_url_name = "herring:index"
    filterset_class = filters.SampleFilter
    template_name = "herring/sample_list.html"
    container_class = "container-fluid"
    row_object_url_name = "herring:sample_detail"
    paginate_by = 100
    h1 = "Herring and Gaspereau Samples"
    new_object_url = reverse_lazy("herring:sample_new")
    field_list = [
        {"name": 'id', },
        {"name": 'type', },
        {"name": 'sample_date', },
        {"name": "sampler_ref_number"},
        {"name": 'survey_id', },
        {"name": 'sampler', },
        {"name": 'port', },
        {"name": 'experimental_net_used', },
        {"name": 'fish_processed|# Fish processed', },
        {"name": 'date_processed|Date processed<br>(yyyy-mm-dd)', },
        {"name": 'lab_complete|Lab complete', },
        {"name": 'otoliths_complete|Otoliths complete', },
    ]

    def get_queryset(self):
        return models.Sample.objects.all().order_by("sample_date")


class SampleSearchFormView(HerringAccess, CommonFormView):
    h1 = "Find a Sample"
    home_url_name = "herring:index"
    template_name = 'herring/form.html'
    submit_text = f"<span class='mr-1 mdi mdi-magnify'></span>Search"
    form_class = forms.FileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = filters.SampleFilter().form
        context["form"].initial = dict(season=timezone.now().year)
        return context

    def form_invalid(self, form):
        qs = filters.SampleFilter(data=form.data).qs
        if qs.count() == 1:
            return HttpResponseRedirect(reverse("herring:sample_detail", args=[qs.first().id]))
        elif not qs.exists():
            messages.error(self.request, "Sorry, there were no samples found using those search criteria")

            return HttpResponseRedirect(reverse("herring:sample_search"))
        else:
            params = listrify([f"{d}={form.data[d]}" for d in form.data if "token" not in d], separator="&")
            return HttpResponseRedirect(reverse("herring:sample_list")+ f"?{params}")


class SampleDetailView(HerringCRUD, CommonDetailView):
    template_name = 'herring/sample_detail/main.html'
    model = models.Sample
    home_url_name = "herring:index"
    parent_crumb = {"title": "Samples", "url": reverse_lazy("herring:sample_list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # pass in the tests
        tests = models.Test.objects.filter(Q(id=205) | Q(id=230) | Q(id=231) | Q(id=232))
        context['tests'] = tests
        context['field_list'] = [
            'type',
            'sample_date',
            'sampler_ref_number',
            'sampler',
            'port',
            'survey_id',
            'latitude_n',
            'longitude_w',
            'fishing_area',
            'gear',
            'experimental_net_used',
            'vessel_cfvn',
            'mesh_size',
            'catch_weight_lbs',
            'sample_weight_lbs',
            'total_fish_measured',
            'total_fish_preserved',
            'old_id',
            'remarks',
            'created_by',
            'creation_date',
            'last_modified_by',
            'last_modified_date',
        ]

        # create a list of length freq counts FOR SAMPLE
        if self.object.length_frequency_objects.count() > 0:
            count_list = []
            for obj in self.object.length_frequency_objects.all():
                count_list.append(obj.count)

            # add the max count as context
            context['max_count'] = max(count_list)

            # add the sum as context
            context['sum_count'] = sum(count_list)

            # add the phrase to read
            playback_string = "Reading back frequency counts. "
            playback_string = playback_string + ", ".join(str(count) for count in count_list)
            context['playback_string'] = playback_string

        # create a list of length freq counts FISH DETAILs
        length_list = []
        for obj in self.object.fish_details.all().order_by("fish_length"):
            if obj.fish_length:
                original_length_cm = obj.fish_length / 10
                integer = math.floor(original_length_cm)
                decimal = (original_length_cm - integer)
                if decimal > 0 and decimal <= 0.5:
                    new_decimal = 0.5
                else:
                    new_decimal = 1
                binned_length = new_decimal + integer

                length_list.append(binned_length)
        if len(length_list) > 0:
            # return a dict of length_bins and corresponding counts
            bin_dict = collections.Counter(length_list)
            bin_list = arange(min(length_list), max(length_list) + 0.5, step=0.5)
            max_fish_detail_count = 0
            sum_fish_detail_count = 0
            for i in range(0, len(bin_list)):
                count = bin_dict[bin_list[i]]
                bin_dict[bin_list[i]] = count
                if count > max_fish_detail_count:
                    max_fish_detail_count = count
                sum_fish_detail_count = sum_fish_detail_count + count
            context['bin_list'] = bin_list
            context['bin_dict'] = bin_dict
            context['max_fish_detail_count'] = max_fish_detail_count
            context['sum_fish_detail_count'] = sum_fish_detail_count

        # provide a list of fish detail lab_processed_dates
        for fishy in self.object.fish_details.all():
            fishy.save()
        # resave the sample instance to run thought sample save method
        self.object.save()
        print(self.object.lab_processing_complete)
        # now conduct the test

        return context


class SampleCreateView(HerringCRUD, CommonCreateView):
    template_name = 'herring/sample_form.html'
    form_class = forms.SampleForm
    model = models.Sample
    home_url_name = "herring:index"
    parent_crumb = {"title": "Samples", "url": reverse_lazy("herring:sample_list")}

    def get_initial(self):
        return {

            'do_another': 1,
        }

    def form_valid(self, form):
        obj = form.save(commit=False)

        obj.created_by = self.request.user
        obj.last_modified_by = self.request.user
        obj.save()

        # port_sample_tests(object)
        if form.cleaned_data["do_another"] == 1:
            return HttpResponseRedirect(reverse_lazy('herring:sample_new'))
        else:
            return HttpResponseRedirect(reverse_lazy('herring:sample_list'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get a list of ports
        port_list = ['<a href="#" class="port_insert" code={}>{}</a>'.format(p.id, p) for p in shared_models.Port.objects.all()]
        context['port_list'] = port_list

        # get a list of samplers
        sampler_list = []
        for s in models.Sampler.objects.all():
            if s.first_name:
                first = s.first_name.replace("'", "")
            else:
                first = None

            if s.last_name:
                last = s.last_name.replace("'", "")
            else:
                last = None

            html_insert = '<a href="#" class="sampler_insert" code={id}>{first} {last}</a>'.format(id=s.id, first=first,
                                                                                                   last=last)
            sampler_list.append(html_insert)
        context['sampler_list'] = sampler_list
        return context


class SampleDeleteView(HerringCRUD, CommonDeleteView):
    template_name = 'herring/confirm_delete.html'
    model = models.Sample
    success_url = reverse_lazy("herring:sample_list")
    delete_protection = False
    home_url_name = "herring:index"
    grandparent_crumb = {"title": "Samples", "url": reverse_lazy("herring:sample_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("herring:sample_detail", args=[self.get_object().id])}


class SampleUpdateView(HerringCRUD, CommonUpdateView):
    template_name = 'herring/sample_form.html'
    form_class = forms.SampleForm
    model = models.Sample
    home_url_name = "herring:index"
    grandparent_crumb = {"title": "Samples", "url": reverse_lazy("herring:sample_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("herring:sample_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        # port_sample_tests(self.object)
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        return super().form_valid(form)


class SamplePopoutUpdateView(HerringCRUD, UpdateView):
    template_name = 'herring/sample_form_popout.html'
    model = models.Sample

    def get_form_class(self):
        if self.kwargs["type"] == "measured":
            return forms.SampleFishMeasuredForm
        elif self.kwargs["type"] == "preserved":
            return forms.SampleFishPreservedForm

    def form_valid(self, form):
        obj = form.save()
        obj.last_modified_by = self.request.user
        obj.save()
        return HttpResponseRedirect(reverse("herring:close_me"))


def move_sample_next(request, sample):
    # shared vars
    message_end = "You are at the last sample."

    sample_list = models.Sample.objects.all().order_by("id")
    record_count = sample_list.count()

    # populate a list with all fish detail ids
    id_list = [s.id for s in sample_list]

    # figure out where the current record is within recordset
    current_index = id_list.index(sample)

    # if you are at the end of the recordset, there is nowhere to go!
    if sample == id_list[-1]:
        messages.success(request, message_end)
        return HttpResponseRedirect(reverse(viewname='herring:sample_detail', kwargs={"pk": sample, }))

    # othersise move forward 1
    else:
        target_id = id_list[current_index + 1]
        return HttpResponseRedirect(reverse(viewname='herring:sample_detail', kwargs={"pk": target_id, }))


# Length Frequeny wizard #
##########################

class LengthFrquencyWizardConfirmation(HerringCRUD, TemplateView):
    template_name = 'herring/length_freq_wizard_confirmation.html'


class LengthFrquencyWizardSetupFormView(HerringCRUD, FormView):
    template_name = 'herring/length_freq_wizard_setup.html'
    form_class = forms.LengthFrquencyWizardSetupForm

    def form_valid(self, form):
        sample = int(self.kwargs["sample"])
        from_length = str(form.cleaned_data['minimum_length'])
        to_length = str(form.cleaned_data['maximum_length'])

        # Delete any existing length frequency data associated with this sample
        models.LengthFrequency.objects.filter(sample_id=sample).delete()

        return HttpResponseRedirect(reverse('herring:lf_wizard', kwargs={
            "sample": sample,
            "from_length": from_length,
            "to_length": to_length,
            "current_length": from_length,
        }))


class LengthFrquencyWizardFormView(HerringCRUD, FormView):
    template_name = 'herring/length_freq_wizard.html'
    form_class = forms.LengthFrquencyWizardForm

    def form_valid(self, form):
        sample = int(self.kwargs["sample"])
        from_length = float(self.kwargs['from_length'])
        to_length = float(self.kwargs['to_length'])
        current_length = float(self.kwargs['current_length'])
        models.LengthFrequency.objects.create(sample_id=sample, length_bin_id=current_length,
                                              count=form.cleaned_data['count'])

        if current_length == to_length:
            # port_sample_tests(models.Sample.objects.get(pk=sample))
            return HttpResponseRedirect(reverse('shared_models:close_me'))
        else:
            return HttpResponseRedirect(reverse('herring:lf_wizard', kwargs={
                "sample": sample,
                "from_length": from_length,
                "to_length": to_length,
                "current_length": str(current_length + 0.5)
            }))


class LengthFrquencyUpdateView(HerringCRUD, UpdateView):
    model = models.LengthFrequency
    template_name = 'herring/length_freq_wizard.html'
    fields = ["count"]

    # form_class = forms.LengthFrquencyWizardForm

    def form_valid(self, form):
        object = form.save()
        # port_sample_tests(object.sample)
        return HttpResponseRedirect(reverse('herring:close_me'))


# FISH DETAIL #
##############

class FishDetailView(HerringCRUD, DetailView):
    template_name = 'herring/fish_detail.html'
    model = models.FishDetail
    home_url_name = "herring:index"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class FishCreateView(HerringCRUD, CreateView):
    template_name = 'herring/fish_form.html'
    form_class = forms.FishForm
    model = models.FishDetail
    home_url_name = "herring:index"

    def get_initial(self):
        return {
            'sample': self.kwargs['sample'],
        }

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.sample = self.request.user
        obj.created_by = self.request.user
        obj.last_modified_by = self.request.user
        return super().form_valid(form)


class FishUpdateView(HerringCRUD, UpdateView):
    template_name = 'herring/fish_form.html'
    form_class = forms.FishForm
    model = models.FishDetail
    home_url_name = "herring:index"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        return super().form_valid(form)


class FishDeleteView(HerringCRUD, DeleteView):
    template_name = 'herring/fish_confirm_delete.html'
    model = models.FishDetail
    home_url_name = "herring:index"

    def get_success_url(self):
        return reverse_lazy('herring:sample_detail', kwargs={'pk': self.kwargs['sample']})


# lab samples

class LabSampleConfirmation(HerringCRUD, TemplateView):
    template_name = 'herring/lab_sample_confirmation.html'


def lab_sample_primer(request, sample):
    # figure out what the fish number is
    my_sample = models.Sample.objects.get(pk=sample)
    if my_sample.fish_details.count() == 0:
        fish_number = 1
    else:
        fish_number = my_sample.fish_details.order_by("fish_number").last().fish_number + 1

    # create new instance of FishDetail with appropriate primed detail
    my_fishy = models.FishDetail.objects.create(created_by=request.user, sample_id=sample, fish_number=fish_number)
    return HttpResponseRedirect(reverse('herring:lab_sample_form', kwargs={
        "sample": sample,
        "pk": my_fishy.id,
    }))


class FishboardTestView(HerringCRUD, TemplateView):
    template_name = 'herring/fishboard_test_form.html'
    home_url_name = "herring:index"


class LabSampleUpdateView(HerringCRUD, UpdateView):
    template_name = 'herring/lab_sample_form.html'
    model = models.FishDetail
    form_class = forms.LabSampleForm
    home_url_name = "herring:index"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # pass in the tests
        tests = models.Test.objects.filter(
            Q(id=201) | Q(id=202) | Q(id=203) | Q(id=204) | Q(id=207) | Q(id=208) | Q(id=300) | Q(id=301) | Q(id=303) | Q(id=304) | Q(
                id=306) | Q(id=307)).order_by("id")
        context['tests'] = tests

        # determine the progress of data entry
        ## there are 6 fields: len, wt, g_wt, sex, mat, parasite; HOWEVER parasites are only looked at from sea samples
        progress = 0
        if self.object.fish_length:
            progress = progress + 1
        if self.object.fish_weight:
            progress = progress + 1
        if self.object.sex:
            progress = progress + 1
        if self.object.maturity:
            progress = progress + 1
        if self.object.gonad_weight != None:
            progress = progress + 1
        if self.object.sample.type == 2:
            if self.object.parasite != None:
                progress = progress + 1
            total_tests = 6
        else:
            total_tests = 5

        context['progress'] = progress
        context['total_tests'] = total_tests

        # determine if this is the last sample in the series
        ## populate a list with all fish detail ids
        id_list = []
        for f in models.FishDetail.objects.filter(sample_id=self.kwargs["sample"]).order_by("id"):
            id_list.append(f.id)

        ##determine if this fish is on the leading edge
        if self.object.id == id_list[-1]:
            context['last_record'] = True
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        obj.lab_sampler = self.request.user
        obj.save()

        print(form.cleaned_data["where_to"])
        if form.cleaned_data["where_to"] == "home":
            return HttpResponseRedirect(reverse("herring:sample_detail", kwargs={'pk': object.sample.id, }))
        elif form.cleaned_data["where_to"] == "prev":
            return HttpResponseRedirect(reverse("herring:move_record",
                                                kwargs={'sample': object.sample.id, "type": "lab", "direction": "prev",
                                                        "current_id": object.id}))
        elif form.cleaned_data["where_to"] == "next":
            return HttpResponseRedirect(reverse("herring:move_record",
                                                kwargs={'sample': object.sample.id, "type": "lab", "direction": "next",
                                                        "current_id": object.id}))
        elif form.cleaned_data["where_to"] == "new":
            return HttpResponseRedirect(reverse("herring:lab_sample_primer", kwargs={'sample': object.sample.id, }))
        else:
            return HttpResponseRedirect(
                reverse("herring:lab_sample_form", kwargs={'sample': object.sample.id, 'pk': object.id}))


# this view should have a progress bar and a button to get started. also should display any issues and messages about the input.

def delete_fish_detail(request, sample, pk):
    fishy = models.FishDetail.objects.get(pk=pk)
    fishy.delete()
    return HttpResponseRedirect(reverse("herring:sample_detail", kwargs={"pk": sample}))


# Otolith

class OtolithUpdateView(HerringCRUD, UpdateView):
    template_name = 'herring/otolith_form.html'
    model = models.FishDetail
    form_class = forms.OtolithForm
    home_url_name = "herring:index"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # pass in the tests
        tests = models.Test.objects.filter(
            Q(id=200) | Q(id=206) | Q(id=209) | Q(id=210) | Q(id=211) | Q(id=309) | Q(id=310)).order_by(
            "id")
        context['tests'] = tests

        # determine the progress of data entry
        ## there are 2 fields: len, wt, g_wt, sex, mat, parasite; HOWEVER parasites are only looked at from sea samples
        progress = 0
        if self.object.annulus_count:
            progress = progress + 1
        if self.object.otolith_season:
            progress = progress + 1
        total_tests = 2

        context['progress'] = progress
        context['total_tests'] = total_tests

        # provide some context about the position of the current record
        try:
            next_fishy = \
                models.FishDetail.objects.filter(sample=self.object.sample, fish_number=self.object.fish_number + 1)[0]
        except Exception as e:
            print(e)
        else:
            context['next_fish_id'] = next_fishy.id

        context["prev_record"] = reverse("herring:move_record",
                                         kwargs={'sample': self.object.sample.id, "type": "otolith",
                                                 "direction": "prev", "current_id": self.object.id})
        context["next_record"] = reverse("herring:move_record",
                                         kwargs={'sample': self.object.sample.id, "type": "otolith",
                                                 "direction": "next", "current_id": self.object.id})
        context["home"] = reverse("herring:sample_detail", kwargs={'pk': self.object.sample.id, })

        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        obj.otolith_sampler = self.request.user
        obj.save()

        if form.cleaned_data["where_to"] == "home":
            return HttpResponseRedirect(reverse("herring:sample_detail", kwargs={'pk': obj.sample.id, }))
        elif form.cleaned_data["where_to"] == "prev":
            return HttpResponseRedirect(reverse("herring:move_record",
                                                kwargs={'sample': obj.sample.id, "type": "otolith",
                                                        "direction": "prev", "current_id": obj.id}))
        elif form.cleaned_data["where_to"] == "next":
            return HttpResponseRedirect(reverse("herring:move_record",
                                                kwargs={'sample': obj.sample.id, "type": "otolith",
                                                        "direction": "next", "current_id": obj.id}))
        else:
            return HttpResponseRedirect(
                reverse("herring:otolith_form", kwargs={'sample': obj.sample.id, 'pk': obj.id}))


# SHARED #
##########
def move_record(request, sample, type, direction, current_id):
    # shared vars
    message_start = "You are at the start of the recordset."
    message_end = "You are at the end of the recordset."

    if type == "lab":
        viewname = "herring:lab_sample_form"
    elif type == "otolith":
        viewname = "herring:otolith_form"

    # prime a listto store ids
    id_list = []

    record_count = models.FishDetail.objects.filter(sample_id=sample).count()

    # populate a list with all fish detail ids
    for f in models.FishDetail.objects.filter(sample_id=sample).order_by("id"):
        id_list.append(f.id)

    # figure out where the current record is within recordset
    current_index = id_list.index(current_id)

    # PgaeUp
    if direction == "prev":
        # if at beginning, cannot go further back!
        if current_index == 0:
            messages.success(request, message_start)
            return HttpResponseRedirect(reverse(viewname=viewname, kwargs={'sample': sample, "pk": current_id, }))
        # otherwise, just move backwards 1
        else:
            target_id = id_list[current_index - 1]
            return HttpResponseRedirect(reverse(viewname=viewname, kwargs={'sample': sample, "pk": target_id}))

    # PageDown
    elif direction == "next":
        # if you are at the end of the recordset, there is nowhere to go!
        if current_id == id_list[-1]:
            messages.success(request, message_end)
            return HttpResponseRedirect(reverse(viewname=viewname, kwargs={'sample': sample, "pk": current_id, }))

        # othersise move forward 1
        else:
            target_id = id_list[current_index + 1]
            return HttpResponseRedirect(reverse(viewname=viewname, kwargs={'sample': sample, "pk": target_id}))


# REPORTS #
###########


class ReportSearchFormView(HerringCRUD, FormView):
    template_name = 'herring/reports.html'
    home_url_name = "herring:index"
    form_class = forms.ReportSearchForm

    def get_initial(self):
        # default the year to the year of the latest samples
        return {
            # "report": 1,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        report = int(form.cleaned_data["report"])
        year = int(form.cleaned_data["year"])

        if report == 1:
            return HttpResponseRedirect(reverse("herring:progress_report_detail", kwargs={'year': year}))
        elif report == 2:
            return HttpResponseRedirect(reverse("herring:export_fish_detail", kwargs={'year': year}))
        elif report == 3:
            return HttpResponseRedirect(reverse("herring:export_hlen", kwargs={'year': year}))
        elif report == 4:
            return HttpResponseRedirect(reverse("herring:export_hlog", kwargs={'year': year}))
        elif report == 5:
            return HttpResponseRedirect(reverse("herring:export_hdet", kwargs={'year': year}))
        elif report == 6:
            return HttpResponseRedirect(reverse("herring:export_sample_report", kwargs={'year': year}))
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("herring:report_search"))


class ProgressReportListView(HerringCRUD, ListView):
    template_name = 'herring/report_progress_list.html'
    home_url_name = "herring:index"

    def get_queryset(self):
        return models.Sample.objects.filter(season=self.kwargs["year"]).order_by("sample_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = models.Sample.objects.filter(season=self.kwargs["year"])

        # sum of samples
        context["sample_sum"] = qs.count

        # sum of fish
        running_total = 0
        for sample in qs:
            running_total = running_total + nz(sample.total_fish_preserved, 0)
        context["fish_sum"] = running_total

        # LAB PROCESSING

        # sum of samples COMPLETE
        context["sample_sum_lab_complete"] = qs.filter(lab_processing_complete=True).count

        # sum of fish COMPLETE
        running_total = 0
        for sample in qs.filter(lab_processing_complete=True):
            running_total = running_total + sample.total_fish_preserved
        context["fish_sum_lab_complete"] = running_total

        # sum of samples REMAINING
        context["sample_sum_lab_remaining"] = qs.filter(lab_processing_complete=False).count

        # sum of fish REMAINING
        running_total = 0
        for sample in qs.filter(lab_processing_complete=False):
            running_total = running_total + nz(sample.total_fish_preserved, 0)
        context["fish_sum_lab_remaining"] = running_total

        # OTOLITH PROCESSING

        # sum of samples COMPLETE
        context["sample_sum_oto_complete"] = qs.filter(otolith_processing_complete=True).count

        # sum of fish COMPLETE
        running_total = 0
        for sample in qs.filter(otolith_processing_complete=True):
            running_total = running_total + nz(sample.total_fish_preserved, 0)
        context["fish_sum_oto_complete"] = running_total

        # sum of samples REMAINING
        context["sample_sum_oto_remaining"] = qs.filter(otolith_processing_complete=False).count

        # sum of fish REMAINING
        running_total = 0
        for sample in qs.filter(otolith_processing_complete=False):
            running_total = running_total + nz(sample.total_fish_preserved, 0)
        context["fish_sum_oto_remaining"] = running_total

        return context


def export_progress_report(request, year):
    response = reports.generate_progress_report(year)
    return response


def export_fish_detail(request, year):
    response = reports.generate_fish_detail_report(year)
    return response


def export_sample_report(request, year):
    response = reports.generate_sample_report(year)
    return response


def export_hlog(request, year):
    response = reports.generate_hlog(year)
    return response


def export_hlen(request, year):
    response = reports.generate_hlen(year)
    return response


def export_hdet(request, year):
    # we will want to let the user know if there is a fish that has not been fully processed in the lab
    fishies = models.FishDetail.objects.filter(sample__season=year, lab_processed_date__isnull=True).order_by("sample__sample_date",
                                                                                                              "fish_number")
    # if there are fish details that are currently incomplete...
    if fishies.exists():
        mylist = []
        for fish in fishies:
            mylist.append(f"<a href='{reverse('herring:fish_detail', args=[fish.sample.id, fish.id])}'>{fish.fish_number}</a>")
        messages.warning(request, mark_safe(
            f'Warning: There are incomplete fish detail records in this query. Those fish will not be returned in the HDET file. {listrify(mylist)}'
        ))

    response = reports.generate_hdet(year)
    return response


# ADMIN #
#########

class CheckUsageListView(HerringAdmin, CommonListView):
    h1 = "Modified Fish Details"
    template_name = "herring/check_usage.html"
    home_url_name = "herring:index"
    model = models.FishDetail
    # show only the top twenty results
    queryset = model.objects.all().order_by('-last_modified_date')[:50]


class ImportFileView(HerringAdmin, CommonFormView):
    fields = "__all__"
    home_url_name = "herring:index"
    form_class = forms.FileForm
    is_multipart_form_data = True

    def get_h1(self):
        if self.kwargs.get("type") == "sample":
            return 'Import Sample Data from ANDES'
        elif self.kwargs.get("type") == "lf":
            return 'Import Length Frequency Data from ANDES'
        elif self.kwargs.get("type") == 'detail':
            return 'Import Detail Data from ANDES'

    def get_template_names(self):
        if self.kwargs.get("type") == "sample":
            return 'herring/import/sample.html'
        if self.kwargs.get("type") == "lf":
            return 'herring/import/lf.html'
        if self.kwargs.get("type") == 'detail':
            return 'herring/import/detail.html'

    def form_valid(self, form):
        temp_file = form.files['file']
        temp_file.seek(0)
        csv_reader = csv.DictReader(StringIO(temp_file.read().decode('utf-8')))

        i = 0
        # loop through each row of the csv file
        for row in csv_reader:
            # what to do if we are importing a sample data export..
            if self.kwargs.get("type") == "sample":
                # each row will represent a sample
                # we only want herring.. so if there is a species field, it should be clupea ...
                species_name = row.get("species")
                if not species_name or species_name.lower().startswith("clupea"):
                    sample_qs = models.Sample.objects.filter(old_id=row.get("uuid"))

                    # let's get or create a sample based on the uuid
                    if sample_qs.exists():
                        my_sample = get_object_or_404(models.Sample, old_id=row.get("uuid"))
                    else:
                        my_sample = models.Sample.objects.create(
                            old_id=row.get("uuid"),
                            sample_date=datetime.strptime(row.get("sample_date"), "%Y-%m-%d %H:%M:%S%z"),
                        )

                    # let's do this easy stuff in one shot:
                    my_sample.type = row.get("type")
                    my_sample.survey_id = nz(row.get("survey_id"), None)
                    my_sample.sampler_ref_number = nz(row.get("sampler_ref_number"), None)
                    my_sample.latitude_n = nz(row.get("latitude_n"), None)
                    my_sample.longitude_w = nz(row.get("longitude_w"), None)
                    my_sample.experimental_net_used = row.get("experimental_net_used")
                    my_sample.sample_weight_lbs = nz(row.get("sample_weight_lbs"), None)
                    my_sample.catch_weight_lbs = nz(row.get("catch_weight_lbs"), None)
                    my_sample.total_fish_measured = nz(row.get("total_fish_measured"), None)
                    my_sample.total_fish_preserved = nz(row.get("total_fish_preserved"), None)
                    my_sample.remarks = nz(row.get("remarks"), None)
                    my_sample.creation_date = datetime.strptime(row.get("creation_date"), "%Y-%m-%d %H:%M:%S%z")
                    my_sample.last_modified_date = datetime.strptime(row.get("last_modified_date"), "%Y-%m-%d %H:%M:%S%z") if row.get(
                        "last_modified_date") else None
                    my_sample.created_by = self.request.user
                    my_sample.last_modified_by = self.request.user
                    my_sample.vessel_cfvn = nz(row.get("vessel_cfvn"), None)

                    # now the trickier stuff:
                    # SAMPLER
                    if row.get("sampler"):
                        sedna_sampler = row.get("sampler").lower().split(" ")  # this will be in the format [last_name, first_name]

                        # look for something similar in the hermorrhage db
                        herm_sampler = models.Sampler.objects.filter(
                            first_name__istartswith=sedna_sampler[0].strip(),
                            last_name__iexact=sedna_sampler[1].strip(),
                        )
                        if herm_sampler.count() == 1:
                            # bingo, we found our man
                            print("bingo, we found our man")
                            my_sample.sampler = herm_sampler.first()
                        elif herm_sampler.count() == 0:
                            print("no hits for sampler")
                            # this user appears to be absent from hermorrhage db
                            new_sampler = models.Sampler.objects.create(first_name=sedna_sampler[1], last_name=sedna_sampler[0])
                            my_sample.sampler = new_sampler
                        else:
                            print("more than one hit for sampler")
                            # we are in a position where there are more than one hits.. try using the whole first name.
                            # if there are still more than one hits we can just choose the first sampler arbitrarily... means there is a duplicate
                            # If no hits probably safer just to create a new sampler
                            herm_sampler = models.Sampler.objects.filter(
                                first_name__iexact=sedna_sampler[1],
                                last_name__iexact=sedna_sampler[0],
                            )
                            if herm_sampler.count() > 0:
                                # bingo, we found our man (after a few adjustments)
                                print("bingo, we found our man (after a few adjustments)")
                                my_sample.sampler = herm_sampler.first()
                            else:
                                print("no hits for sampler, when using full first name")
                                # this user appears to be absent from hermorrhage db
                                new_sampler = models.Sampler.objects.create(first_name=sedna_sampler[1], last_name=sedna_sampler[0])
                                my_sample.sampler = new_sampler
                    else:
                        herm_sampler, created = models.Sampler.objects.get_or_create(last_name="UNKNOWN")  # sampler = UNKNOWN
                        my_sample.sampler = herm_sampler

                    # FISHING AREA
                    # since this is more fundamental, let's crush the script is not found
                    # look for something exactly the same in the hermorrhage db
                    if row.get("fishing_area"):
                        my_sample.fishing_area = models.FishingArea.objects.get(nafo_area_code__iexact=row.get("fishing_area"))

                    # GEAR
                    # same for gear. not finding something here is unacceptable
                    if row.get("gear"):
                        my_sample.gear = models.Gear.objects.get(gear_code__iexact=row.get("gear"))

                    # MESH SIZE
                    if row.get("mesh_size"):
                        try:
                            my_mesh = models.MeshSize.objects.get(size_mm=row.get("mesh_size"))
                        except models.MeshSize.DoesNotExist:
                            my_mesh = models.MeshSize.objects.create(
                                size_mm=row.get("mesh_size")
                            )
                        my_sample.mesh_size = my_mesh

                    # PORT
                    if row.get("port_code"):
                        # not finding something here is unacceptable
                        for port in shared_models.Port.objects.all():
                            if row.get("port_code") == port.full_code:
                                my_sample.port = port
                                break

                    my_sample.save()
                else:
                    messages.warning(self.request,
                                     "Skipping sample with uuid {} because it is not a herring sample.".format(row.get("uuid")))
            elif self.kwargs.get("type") == "lf":
                # each row will represent a length frequency object
                # let's get the sample based on the uuid; if not found we should crash because something went wrong
                try:
                    my_sample = models.Sample.objects.get(old_id=row.get("sample_uuid"))
                except models.Sample.DoesNotExist:
                    messages.warning(self.request,
                                     "Sample with uuid {} was not found in the hermorrhage db. This length frequecy will be skipped".format(
                                         row.get("sample_uuid")))
                else:
                    if i == 0:
                        my_sample.length_frequency_objects.all().delete()
                    my_lf, created = models.LengthFrequency.objects.get_or_create(
                        sample=my_sample,
                        length_bin_id=row.get("length_bin"),
                    )
                    my_lf.count = row.get("count")
                    my_lf.save()
                    my_sample.save()  # run the save method to do a few updates

            elif self.kwargs.get("type") == "detail":
                # each row will represent a fish detail
                # let's get the sample based on the uuid; if not found we should crash because something went wrong
                my_sample = models.Sample.objects.get(old_id=row.get("sample_uuid"))

                # DJF: I DON'T HAVE THE TIME TO COMPLETE THIS RIGHT NOW. THIS YEAR (2019) THERE WERE NO FISH DETAIL RECORDS
                # PROCCESSED IN SEDNA SO I WILL KICK THE CAN DOWN UNTIL A LATER DATE
                # Note: this import scirpt is a combination of the sample import and the lf import above.
                messages.info(self.request,
                              "Due to limited time resources, this import script was not developed. Once fish details are process on "
                              "boats, this function will be built")
            i += 1

        # clear the file in my object
        return HttpResponseRedirect(reverse('herring:index'))
