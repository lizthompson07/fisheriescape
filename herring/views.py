from django.shortcuts import render
import csv
from django.shortcuts import render
from django.views.generic import ListView,  UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, AccessMixin
from braces.views import GroupRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django_filters.views import FilterView
from django.utils import timezone
from . import models
from . import forms
from . import filters
from . import emails
# Create your views here.

class IndexView(GroupRequiredMixin,TemplateView):
    template_name = 'herring/index.html'
    group_required = [u"grais_access",]
    login_url = '/accounts/login_required/'

class CloserTemplateView(TemplateView):
    template_name = 'herring/close_me.html'


# QUALITY CONTROL #
###################

def retest_sample(request, sample):
    s = models.Sample.objects.get(pk=sample)
    port_sample_tests(s)
    return HttpResponseRedirect(reverse('herring:port_sample_detail', kwargs={"pk":sample}))

def port_sample_tests(sample):
    # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
    models.SampleTest.objects.filter(sample_id=sample.id).delete()

    # CREATE BLANK TESTS IN SAMPLETEST
    sample_test_202 = models.SampleTest.objects.create(sample_id=sample.id,test_id=202,test_passed=False)
    sample_test_205 = models.SampleTest.objects.create(sample_id=sample.id,test_id=205,test_passed=False)

    # RUN TEST 202 FOR PORT SAMPLE
    if sample.sampling_protocol and sample.sample_date and sample.sampler and sample.sampler_ref_number and sample.total_fish_preserved and sample.total_fish_measured:
        sample_test_202.test_passed = True
        sample_test_202.save()

    # RUN TEST 205 FOR PORT SAMPLE
    # get list of counts
    count_list = []
    for obj in sample.length_frequency_objects.all():
        count_list.append(obj.count)
    # add the sum as context
    count_sum = sum(count_list)

    if count_sum == sample.total_fish_measured:
        sample_test_205.test_passed = True
        sample_test_205.save()



# SAMPLE #
##########
class SampleFilterView(LoginRequiredMixin, FilterView):
    filterset_class = filters.SampleFilter
    template_name = "herring/sample_filter.html"
    login_url = '/accounts/login_required/'

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"SeasonSince": timezone.now().year-1 }
        return kwargs

class PortSampleCreateView(LoginRequiredMixin,CreateView):
    template_name = 'herring/port_sample_form.html'
    form_class = forms.PortSampleForm
    model = models.Sample

    def get_initial(self):
        return {
            'created_by': self.request.user,
            'last_modified_by': self.request.user,
        }

    def form_valid(self, form):
        object = form.save()
        port_sample_tests(object)
        return super().form_valid(form)

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

class PortSampleDetailView(LoginRequiredMixin,DetailView):
    template_name = 'herring/port_sample_detail.html'
    model = models.Sample

    # def dispatch(request, *args, **kwargs):
    #     port_sample_tests(self.object)
    #     return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        port_sample_tests(self.object)

        # create a list of length freq counts
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
