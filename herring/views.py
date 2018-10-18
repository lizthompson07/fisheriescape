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
import json
from . import models
from . import forms
from . import filters
from . import emails
from . import quality_control
# Create your views here.

class IndexView(GroupRequiredMixin,TemplateView):
    template_name = 'herring/index.html'
    group_required = [u"herring_access",]
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
    success_url = reverse_lazy("herring:close_me")
    #
    # def form_valid(self, form):
    #     object = form.save()
    #     return HttpResponseRedirect(reverse("herring:close_me"))


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["add_sampler_href"] = reverse("herring:sampler_new_pop")

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


class LabSampleUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'herring/lab_sample_form.html'
    model = models.FishDetail
    form_class = forms.LabSampleForm
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # run the quality test on loading the data
        my_dict = lab_sample_tests(self.object)

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

        qc_feedback_json = json.dumps(my_dict)

        # send JSON file to template so that it can be used by js script
        context['qc_feedback_json'] = qc_feedback_json



        # pass in a variable to help determine if the record is complete from a QC point of view
        ## Should be able to make this assessment via the global tests

        context['test_201'] = self.object.sample_tests.filter(test_id=201).first().test_passed



        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'lab_sampler': self.request.user,
            }

    def form_valid(self, form):
        # port_sample_tests(self.object)
        object = form.save()
        if form.cleaned_data["improbable_accepted"]:
            field_name = form.cleaned_data["improbable_field"]
            test_id = form.cleaned_data["improbable_test"]

            # this means that an improbable measurement has been accepted.
            if "global" in field_name:
                my_test = models.FishDetailTest.objects.filter(fish_detail_id=object.id, test_id=test_id).first()
            else:
                my_test = models.FishDetailTest.objects.filter(fish_detail_id=object.id, field_name=field_name, test_id=test_id).first()

            my_test.accepted = True
            my_test.save()
        return HttpResponseRedirect(reverse("herring:lab_sample_form", kwargs={'sample':object.sample.id, 'pk':object.id}))

# this view should have a progress bar and a button to get started. also should display any issues and messages about the input.



# Otolith

class OtolithUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'herring/otolith_form.html'
    model = models.FishDetail
    form_class = forms.OtolithForm
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # run the quality test on loading the data
        my_dict = otolith_tests(self.object)

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

        qc_feedback_json = json.dumps(my_dict)

        # send JSON file to template so that it can be used by js script
        context['qc_feedback_json'] = qc_feedback_json
        try:
            next_fishy = models.FishDetail.objects.filter(sample=self.object.sample, fish_number=self.object.fish_number+1)[0]
        except Exception as e:
            print(e)
        else:
            context['next_fish_id'] = next_fishy.id

        # pass in a variable to help determine if the record is complete from a QC point of view
        ## Should be able to make this assessment via the global tests

        context['test_200'] = self.object.sample_tests.filter(test_id=200).first().test_passed

        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'otolith_sampler': self.request.user,
            }

    def form_valid(self, form):
        # port_sample_tests(self.object)
        object = form.save()
        if form.cleaned_data["improbable_accepted"]:
            field_name = form.cleaned_data["improbable_field"]
            test_id = form.cleaned_data["improbable_test"]

            # this means that an improbable measurement has been accepted.
            if "global" in field_name:
                my_test = models.FishDetailTest.objects.filter(fish_detail_id=object.id, test_id=test_id).first()
            else:
                my_test = models.FishDetailTest.objects.filter(fish_detail_id=object.id, field_name=field_name, test_id=test_id).first()

            my_test.accepted = True
            my_test.save()
        return HttpResponseRedirect(reverse("herring:otolith_form", kwargs={'sample':object.sample.id, 'pk':object.id}))

# this view should have a progress bar and a button to get started. also should display any issues and messages about the input.


# def next_object_in_model(qs,sample,current_pk):
#     kill = False
#     for object in qs:
#         if kill == True:
#             return object.id
#             print("printing object ID")
#             break
#         else:
#             if object.id == current_pk:
#                 kill=True
#     return qs[0].id
#
# def get_new_pk(request, sample, current_pk):
#     qs = models.FishDetail.objects.filter(sample_id=sample).order_by('fish_number')
#
#     try:
#         next_pk = next_object_in_model(qs,sample,current_pk)
#     except :
#         messages.success(request, "All done!!")
#         return HttpResponseRedirect(redirect_to=reverse(viewname='books:transaction_list'))
#     else:
#         if next_pk == None:
#             messages.success(request, "All done!!")
#             return HttpResponseRedirect(redirect_to=reverse(viewname='books:transaction_list'))
#         else:
#             return HttpResponseRedirect(redirect_to=reverse(viewname='books:new_review_item', kwargs={'pk':next_pk}))



# SHARED #
##########


def move_record(request, sample, type, direction, current_id):
    # shared vars
    message_start = "You are at the start of the recordset."
    message_end = "You are at the end of the recordset."

    if type == "lab":
        viewname = "herring:lab_sample_form"
    else:
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
