from django.views.generic import   UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, AccessMixin
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django_filters.views import FilterView
from django.utils import timezone

from . import models
from . import forms
from . import filters
from . import quality_control

from numpy import arange, histogram
import math
import collections
# Create your views here.

def not_in_herring_group(user):
    if user:
        return user.groups.filter(name='herring_access').count() != 0
#
@login_required(login_url = '/accounts/login_required/')
@user_passes_test(not_in_herring_group, login_url='/accounts/denied/')
def index(request):
    return render(request, 'herring/index.html')

# class IndexView(AnonymousRequiredMixin,TemplateView):
#     template_name = 'herring/index.html'
    # group_required = [u"herring_access",]
    # login_url = '/accounts/login_required/'


class CloserTemplateView(TemplateView):
    template_name = 'herring/close_me.html'


# QUALITY CONTROL #
###################

def port_sample_tests(sample):
    quality_control.run_test_mandatory_fields(sample,"port_sample")
    quality_control.run_test_205(sample)
    quality_control.run_test_231(sample)
    quality_control.run_test_232(sample)


def lab_sample_tests(fish_detail):
    my_dict = {}
    my_dict["fish_length"] = quality_control.run_data_point_tests(fish_detail, field_name="fish_length")
    my_dict["fish_weight"] = quality_control.run_data_point_tests(fish_detail, field_name="fish_weight")
    my_dict["gonad_weight"] = quality_control.run_data_point_tests(fish_detail, field_name="gonad_weight")
    quality_control.run_test_mandatory_fields(fish_detail,"lab_sample")
    quality_control.run_test_possible_range(fish_detail,"lab_sample")
    my_dict["global_204"] = quality_control.run_test_204(fish_detail)
    my_dict["global_207"] = quality_control.run_test_207(fish_detail)
    quality_control.run_test_improbable_accepted(fish_detail,"lab_sample")
    quality_control.run_test_qc_passed(fish_detail,"lab_sample")

    return my_dict

def otolith_tests(fish_detail):
    my_dict = {}
    my_dict["annulus_count"] = quality_control.run_data_point_tests(fish_detail, field_name="annulus_count")
    quality_control.run_test_mandatory_fields(fish_detail,"otolith") # mandatory fields
    quality_control.run_test_possible_range(fish_detail,"otolith") # possible range
    my_dict["global_209"] = quality_control.run_test_209(fish_detail) # annulus_count length ratio
    quality_control.run_test_improbable_accepted(fish_detail,"otolith") # improbable obs accepted
    quality_control.run_test_qc_passed(fish_detail,"otolith") # all tests passed

    return my_dict

# SAMPLER #
###########

class SamplerPopoutCreateView(LoginRequiredMixin,CreateView):
    template_name = 'herring/sampler_form_popout.html'
    model = models.Sampler
    form_class = forms.SamplerForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy("herring:close_sampler", kwargs={"sampler":object.id}))

class SamplerCloseTemplateView(TemplateView):
    template_name = 'herring/sampler_close.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = models.Sampler.objects.get(pk = self.kwargs["sampler"])
        context["object"]= object
        return context

# PORT SAMPLE #
###############
class SampleFilterView(LoginRequiredMixin, FilterView):
    filterset_class = filters.SampleFilter
    template_name = "herring/sample_filter.html"
    login_url = '/accounts/login_required/'

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"season": timezone.now().year }
        return kwargs

class PortSampleCreateView(LoginRequiredMixin,CreateView):
    template_name = 'herring/port_sample_form.html'
    form_class = forms.PortSampleForm
    model = models.Sample

    def get_initial(self):
        return {
            'created_by': self.request.user,
            'last_modified_by': self.request.user,
            'do_another': 1,
        }

    def form_valid(self, form):
        object = form.save()
        port_sample_tests(object)
        if form.cleaned_data["do_another"] == 1:
            return HttpResponseRedirect(reverse_lazy('herring:port_sample_new'))
        else:
            return HttpResponseRedirect(reverse_lazy('herring:sample_list'))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get a list of districts
        district_list = []
        for d in models.District.objects.all():
            for l in d.locality_list.split(", "):
                html_insert = '<a href="#" class="district_insert" code={p}{d}>{p}{d}</a> - {l}, {prov}'.format(p=d.province_id,d=d.district_id, l=l.replace("'",""),prov=d.get_province_id_display().upper())
                district_list.append(html_insert)
        context['district_list'] = district_list

        # get a list of samplers
        sampler_list = []
        for s in models.Sampler.objects.all():
            if s.first_name:
                first = s.first_name.replace("'","")
            else:
                first = None

            if s.last_name:
                last = s.last_name.replace("'","")
            else:
                last = None

            html_insert = '<a href="#" class="sampler_insert" code={id}>{first} {last}</a>'.format(id=s.id,first=first, last=last)
            sampler_list.append(html_insert)
        context['sampler_list'] = sampler_list
        return context

class PortSampleDeleteView(LoginRequiredMixin,DeleteView):
    template_name = 'herring/sample_confirm_delete.html'
    model = models.Sample
    success_url = reverse_lazy("herring:sample_list")


class PortSampleUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'herring/port_sample_form.html'
    form_class = forms.PortSampleForm
    model = models.Sample

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            }

    def form_valid(self, form):
        port_sample_tests(self.object)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get a list of districts
        district_list = []
        for d in models.District.objects.all():
            for l in d.locality_list.split(", "):
                html_insert = '<a href="#" class="district_insert" code={p}{d}>{p}{d}</a> - {l}, {prov}'.format(p=d.province_id,d=d.district_id, l=l.replace("'",""),prov=d.get_province_id_display().upper())
                district_list.append(html_insert)
        context['district_list'] = district_list

        # get a list of samplers
        sampler_list = []
        for s in models.Sampler.objects.all():
            if s.first_name:
                first = s.first_name.replace("'","")
            else:
                first = None

            if s.last_name:
                last = s.last_name.replace("'","")
            else:
                last = None

            html_insert = '<a href="#" class="sampler_insert" code={id}>{first} {last}</a>'.format(id=s.id,first=first, last=last)
            sampler_list.append(html_insert)
        context['sampler_list'] = sampler_list
        return context

class PortSamplePopoutUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'herring/port_sample_form_popout.html'
    model = models.Sample

    def get_form_class(self):
        if self.kwargs["type"] == "measured":
            return forms.PortSampleFishMeasuredForm
        elif self.kwargs["type"] == "preserved":
            return forms.PortSampleFishPreservedForm

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            }

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse("herring:close_me"))


class PortSampleDetailView(LoginRequiredMixin,DetailView):
    template_name = 'herring/port_sample_detail.html'
    model = models.Sample


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # pass in the tests
        tests = models.Test.objects.filter(Q(id=205) | Q(id=230) | Q(id=231) | Q(id=232) )
        context['tests'] = tests

        # create a list of length freq counts FOR SAMPLE
        if self.object.length_frequency_objects.count()>0:
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
                original_length_cm = obj.fish_length/10
                integer = math.floor(original_length_cm)
                decimal = (original_length_cm - integer)
                if decimal > 0 and  decimal <= 0.5:
                    new_decimal = 0.5
                else:
                    new_decimal = 1
                binned_length = new_decimal+integer

                length_list.append(binned_length)
        if len(length_list) > 0:
            # return a dict of length_bins and corresponding counts
            bin_dict = collections.Counter(length_list)
            bin_list = arange(min(length_list),max(length_list)+0.5, step=0.5)
            max_fish_detail_count = 0
            sum_fish_detail_count = 0
            for i in range(0,len(bin_list)):
                count = bin_dict[bin_list[i]]
                bin_dict[bin_list[i]]=count
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

# Length Frequeny wizard #
##########################

class LengthFrquencyWizardConfirmation(TemplateView):
    template_name = 'herring/length_freq_wizard_confirmation.html'

class LengthFrquencyWizardSetupFormView(FormView):
    template_name = 'herring/length_freq_wizard_setup.html'
    form_class = forms.LengthFrquencyWizardSetupForm

    def form_valid(self, form):
        sample = int(self.kwargs["sample"])
        from_length = str(form.cleaned_data['minimum_length'])
        to_length = str(form.cleaned_data['maximum_length'])

        # Delete any existing length frequency data associated with this sample
        models.LengthFrequency.objects.filter(sample_id=sample).delete()

        return HttpResponseRedirect(reverse('herring:lf_wizard', kwargs={
            "sample":sample,
            "from_length":from_length,
            "to_length":to_length,
            "current_length":from_length,
        }))

class LengthFrquencyWizardFormView(FormView):
    template_name = 'herring/length_freq_wizard.html'
    form_class = forms.LengthFrquencyWizardForm

    def form_valid(self, form):
        sample = int(self.kwargs["sample"])
        from_length = float(self.kwargs['from_length'])
        to_length = float(self.kwargs['to_length'])
        current_length = float(self.kwargs['current_length'])
        models.LengthFrequency.objects.create(sample_id=sample,length_bin_id=current_length,count=form.cleaned_data['count'])


        if current_length == to_length:
            port_sample_tests(models.Sample.objects.get(pk=sample))
            return HttpResponseRedirect(reverse('herring:close_me'))
        else:
            return HttpResponseRedirect(reverse('herring:lf_wizard', kwargs={
                "sample":sample,
                "from_length":from_length,
                "to_length":to_length,
                "current_length":str(current_length+0.5)
            }))

class LengthFrquencyUpdateView(UpdateView):
    model = models.LengthFrequency
    template_name = 'herring/length_freq_wizard.html'
    fields = ["count"]
    # form_class = forms.LengthFrquencyWizardForm

    def form_valid(self, form):
        object = form.save()
        port_sample_tests(object.sample)
        return HttpResponseRedirect(reverse('herring:close_me'))

# FISH DETAIL #
##############

class FishDetailView(DetailView):
    template_name = 'herring/fish_detail.html'
    model = models.FishDetail

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class FishCreateView(LoginRequiredMixin,CreateView):
    template_name = 'herring/fish_form.html'
    form_class = forms.FishForm
    model = models.FishDetail

    def get_initial(self):
        return {
            'sample': self.kwargs['sample'],
            'created_by': self.request.user,
            'last_modified_by': self.request.user,
        }


class FishUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'herring/fish_form.html'
    form_class = forms.FishForm
    model = models.FishDetail
    login_url = '/accounts/login_required/'


    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }

class FishDeleteView(LoginRequiredMixin,DeleteView):
    template_name = 'herring/fish_confirm_delete.html'
    model = models.FishDetail

    def get_success_url(self):
        return reverse_lazy('herring:port_sample_detail', kwargs={'pk':self.kwargs['sample']})



# lab samples

class LabSampleConfirmation(LoginRequiredMixin, TemplateView):
    template_name = 'herring/lab_sample_confirmation.html'
    login_url = '/accounts/login_required/'


def lab_sample_primer(request, sample):
    # figure out what the fish number is
    my_sample = models.Sample.objects.get(pk=sample)
    if my_sample.fish_details.count() == 0 :
        fish_number = 1
    else:
        fish_number = my_sample.fish_details.order_by("fish_number").last().fish_number + 1

    # create new instance of FishDetail with appropriate primed detail
    my_fishy = models.FishDetail.objects.create(created_by=request.user, sample_id =sample, fish_number=fish_number)
    return HttpResponseRedirect(reverse('herring:lab_sample_form', kwargs={
        "sample":sample,
        "pk":my_fishy.id,
    }))

class FishboardTestView(LoginRequiredMixin,TemplateView):
    template_name = 'herring/fishboard_test_form.html'
    login_url = '/accounts/login_required/'



class LabSampleUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'herring/lab_sample_form.html'
    model = models.FishDetail
    form_class = forms.LabSampleForm
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # pass in the tests
        tests = models.Test.objects.filter(Q(id=201) | Q(id=202) | Q(id=203) | Q(id=204) | Q(id=207) | Q(id=208) | Q(id=300) | Q(id=301) | Q(id=302) | Q(id=303)| Q(id=304)| Q(id=305)| Q(id=306)| Q(id=307)| Q(id=308) ).order_by("id")
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
        if self.object.sample.sampling_protocol.sampling_type == 2:
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


    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'lab_sampler': self.request.user,
            }

    def form_valid(self, form):
        object = form.save()
        print(form.cleaned_data["where_to"])
        if form.cleaned_data["where_to"] == "home":
            return HttpResponseRedirect(reverse("herring:port_sample_detail", kwargs={'pk':object.sample.id,}))
        elif form.cleaned_data["where_to"] == "prev":
            return HttpResponseRedirect(reverse("herring:move_record", kwargs={'sample':object.sample.id,"type":"lab","direction":"prev", "current_id":object.id}))
        elif form.cleaned_data["where_to"] == "next":
            return HttpResponseRedirect(reverse("herring:move_record", kwargs={'sample':object.sample.id,"type":"lab","direction":"next", "current_id":object.id}))
        elif form.cleaned_data["where_to"] == "new":
            return HttpResponseRedirect(reverse("herring:lab_sample_primer", kwargs={'sample':object.sample.id,}))
        else:
            return HttpResponseRedirect(reverse("herring:lab_sample_form", kwargs={'sample':object.sample.id, 'pk':object.id}))



# this view should have a progress bar and a button to get started. also should display any issues and messages about the input.

def delete_fish_detail(request, sample, pk):
    fishy = models.FishDetail.objects.get(pk=pk)
    fishy.delete()
    return HttpResponseRedirect(reverse("herring:port_sample_detail", kwargs = {"pk":sample}))


# Otolith

class OtolithUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'herring/otolith_form.html'
    model = models.FishDetail
    form_class = forms.OtolithForm
    login_url = '/accounts/login_required/'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # pass in the tests
        tests = models.Test.objects.filter(Q(id=200) | Q(id=206) | Q(id=209) | Q(id=210) | Q(id=211) | Q(id=309) | Q(id=310) | Q(id=311)  ).order_by("id")
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
            next_fishy = models.FishDetail.objects.filter(sample=self.object.sample, fish_number=self.object.fish_number+1)[0]
        except Exception as e:
            print(e)
        else:
            context['next_fish_id'] = next_fishy.id

        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'otolith_sampler': self.request.user,
            }

    def form_valid(self, form):
        # port_sample_tests(self.object)
        object = form.save()
        if form.cleaned_data["where_to"] == "home":
            return HttpResponseRedirect(reverse("herring:port_sample_detail", kwargs={'pk':object.sample.id,}))
        elif form.cleaned_data["where_to"] == "prev":
            return HttpResponseRedirect(reverse("herring:move_record", kwargs={'sample':object.sample.id,"type":"otolith","direction":"prev", "current_id":object.id}))
        elif form.cleaned_data["where_to"] == "next":
            return HttpResponseRedirect(reverse("herring:move_record", kwargs={'sample':object.sample.id,"type":"otolith","direction":"next", "current_id":object.id}))
        else:
            return HttpResponseRedirect(reverse("herring:otolith_form", kwargs={'sample':object.sample.id, 'pk':object.id}))


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
            return HttpResponseRedirect(reverse(viewname=viewname, kwargs={'sample':sample, "pk":current_id,}))
        # otherwise, just move backwards 1
        else:
            target_id = id_list[current_index-1]
            return HttpResponseRedirect(reverse(viewname=viewname, kwargs={'sample':sample, "pk":target_id}))

    # PageDown
    elif direction == "next":
        # if you are at the end of the recordset, there is nowhere to go!
        if current_id == id_list[-1]:
            messages.success(request, message_end)
            return HttpResponseRedirect(reverse(viewname=viewname, kwargs={'sample':sample, "pk":current_id,}))

        # othersise move forward 1
        else:
            target_id = id_list[current_index+1]
            return HttpResponseRedirect(reverse(viewname=viewname, kwargs={'sample':sample, "pk":target_id}))
