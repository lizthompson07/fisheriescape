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
from . import quality_control
# Create your views here.

class IndexView(GroupRequiredMixin,TemplateView):
    template_name = 'herring/index.html'
    group_required = [u"grais_access",]
    login_url = '/accounts/login_required/'

class CloserTemplateView(TemplateView):
    template_name = 'herring/close_me.html'


# QUALITY CONTROL #
###################

# def retest_sample(request, sample):
#     s = models.Sample.objects.get(pk=sample)
#     port_sample_tests(s)
#     return HttpResponseRedirect(reverse('herring:port_sample_detail', kwargs={"pk":sample}))

def port_sample_tests(sample):
    quality_control.run_test_202(sample,"port_sample")
    quality_control.run_test_205(sample,"port_sample")
    quality_control.run_test_231(sample,"port_sample")
    quality_control.run_test_232(sample,"port_sample")


def lab_sample_tests(fish_detail):
    quality_control.run_data_point_tests(fish_detail, field_name="fish_length")
    quality_control.run_data_point_tests(fish_detail, field_name="fish_weight")
    quality_control.run_data_point_tests(fish_detail, field_name="gonad_weight")
    quality_control.run_test_202(fish_detail,"lab_sample")
    quality_control.run_test_203(fish_detail,"lab_sample")
    quality_control.run_test_204(fish_detail,"lab_sample")
    quality_control.run_test_207(fish_detail,"lab_sample")
    quality_control.run_test_208(fish_detail,"lab_sample")

# PORT SAMPLE #
###############
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

class LabSampleConfirmation(TemplateView):
    template_name = 'herring/lab_sample_confirmation.html'


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


class LabSampleUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'herring/lab_sample_form.html'
    model = models.FishDetail
    form_class = forms.LabSampleForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # run the quality test on loading the data
        lab_sample_tests(self.object)
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
        if self.object.gonad_weight:
            progress = progress + 1
        if self.object.sample.sampling_protocol.sampling_type == 2:
            if self.object.parasite != None:
                progress = progress + 1
            total_tests = 6
        else:
            total_tests = 5

        context['progress'] = progress
        context['total_tests'] = total_tests
        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'lab_sampler': self.request.user,
            }

    def form_valid(self, form):
        # port_sample_tests(self.object)
        object = form.save()
        return HttpResponseRedirect(reverse("herring:lab_sample_form", kwargs={'sample':object.sample.id, 'pk':object.id}))

# this view should have a progress bar and a button to get started. also should display any issues and messages about the input.
