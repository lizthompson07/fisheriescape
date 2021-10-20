from datetime import datetime

from django.db import IntegrityError
from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy, gettext as _

from lib.functions.custom_functions import listrify
from res.mixins import LoginAccessRequiredMixin, ResAdminRequiredMixin, CanModifyApplicationRequiredMixin, CanViewApplicationRequiredMixin
from shared_models.views import CommonTemplateView, CommonFormsetView, CommonHardDeleteView, CommonCreateView, CommonFilterView, CommonDetailView, \
    CommonUpdateView, CommonDeleteView
from . import models, forms, filters, utils, emails
from .utils import in_res_admin_group


class IndexTemplateView(LoginAccessRequiredMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'res/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_res_admin_group(self.request.user)
        return context


# REFERENCE TABLES /  FORMSETS

class ContextFormsetView(ResAdminRequiredMixin, CommonFormsetView):
    template_name = 'res/formset.html'
    h1 = "Manage Contexts"
    queryset = models.Context.objects.all()
    formset_class = forms.ContextFormset
    success_url_name = "res:manage_contexts"
    home_url_name = "res:index"
    delete_url_name = "res:delete_context"


class ContextHardDeleteView(ResAdminRequiredMixin, CommonHardDeleteView):
    model = models.Context
    success_url = reverse_lazy("res:manage_contexts")


class OutcomeFormsetView(ResAdminRequiredMixin, CommonFormsetView):
    template_name = 'res/formset.html'
    h1 = "Manage Valued Outcomes"
    queryset = models.Outcome.objects.all()
    formset_class = forms.OutcomeFormset
    success_url_name = "res:manage_outcomes"
    home_url_name = "res:index"
    delete_url_name = "res:delete_outcome"


class OutcomeHardDeleteView(ResAdminRequiredMixin, CommonHardDeleteView):
    model = models.Outcome
    success_url = reverse_lazy("res:manage_outcomes")


class AchievementCategoryFormsetView(ResAdminRequiredMixin, CommonFormsetView):
    template_name = 'res/formset.html'
    h1 = "Manage Achievement Categories"
    queryset = models.AchievementCategory.objects.all()
    formset_class = forms.AchievementCategoryFormset
    success_url_name = "res:manage_achievement_categories"
    home_url_name = "res:index"
    delete_url_name = "res:delete_achievement_category"


class AchievementCategoryHardDeleteView(ResAdminRequiredMixin, CommonHardDeleteView):
    model = models.AchievementCategory
    success_url = reverse_lazy("res:manage_achievement_categories")


class GroupLevelFormsetView(ResAdminRequiredMixin, CommonFormsetView):
    template_name = 'res/formset.html'
    h1 = "Manage Group / Levels"
    queryset = models.GroupLevel.objects.all()
    formset_class = forms.GroupLevelFormset
    success_url_name = "res:manage_group_levels"
    home_url_name = "res:index"
    delete_url_name = "res:delete_group_level"


class GroupLevelHardDeleteView(ResAdminRequiredMixin, CommonHardDeleteView):
    model = models.GroupLevel
    success_url = reverse_lazy("res:manage_group_levels")


class PublicationTypeFormsetView(ResAdminRequiredMixin, CommonFormsetView):
    template_name = 'res/formset.html'
    h1 = "Manage Publication Types"
    queryset = models.PublicationType.objects.all()
    formset_class = forms.PublicationTypeFormset
    success_url_name = "res:manage_publication_types"
    home_url_name = "res:index"
    delete_url_name = "res:delete_publication_type"


class PublicationTypeHardDeleteView(ResAdminRequiredMixin, CommonHardDeleteView):
    model = models.PublicationType
    success_url = reverse_lazy("res:manage_publication_types")


# APPLICATIONS
##############


class ApplicationListView(LoginAccessRequiredMixin, CommonFilterView):
    template_name = 'res/list.html'
    filterset_class = filters.ApplicationFilter
    paginate_by = 25
    home_url_name = "res:index"
    new_object_url = reverse_lazy("res:application_new")
    row_object_url_name = row_ = "res:application_detail"
    container_class = "container-fluid"

    field_list = [
        {"name": 'id', "class": "", "width": "50px"},
        {"name": 'fiscal_year', "class": ""},
        {"name": 'applicant', "class": ""},
        {"name": 'target_group_level', "class": ""},
        {"name": 'status', "class": ""},
        {"name": 'region|{}'.format(gettext_lazy("region")), "class": ""},
        {"name": 'section|{}'.format(gettext_lazy("section")), "class": ""},
    ]

    # def get_extra_button_dict1(self):
    #     qs = self.filterset.qs
    #     ids = listrify([obj.id for obj in qs])
    #     return {
    #         "name": _("<span class=' mr-1 mdi mdi-file-excel'></span> {name}").format(name=_("Export")),
    #         "url": reverse("res:application_list_report") + f"?csas_requests={ids}",
    #         "class": "btn-outline-dark",
    #     }

    def get_queryset(self):
        if not in_res_admin_group(self.request.user):
            qs = utils.get_related_applications(self.request.user)
        else:
            qs = models.Application.objects.all()
        return qs

    def get_h1(self):
        if not in_res_admin_group(self.request.user):
            return _("My Applications")
        return _("Applications")



class ApplicationDetailView(CanViewApplicationRequiredMixin, CommonDetailView):
    model = models.Application
    template_name = 'res/application_detail/main.html'
    home_url_name = "res:index"
    parent_crumb = {"title": gettext_lazy("Applications"), "url": reverse_lazy("res:application_list")}
    container_class = " "

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = super().get_context_data(**kwargs)
        return context


class ApplicationCreateView(LoginAccessRequiredMixin, CommonCreateView):
    model = models.Application
    form_class = forms.ApplicationForm
    template_name = 'res/form.html'
    home_url_name = "res:index"
    parent_crumb = {"title": gettext_lazy("Applications"), "url": reverse_lazy("res:application_list")}
    submit_text = gettext_lazy("Save")
    h1 = gettext_lazy("New Application")
    h2 = gettext_lazy("All fields are mandatory before approvals and submission")

    def get_initial(self):
        return dict(
            applicant=self.request.user,
            application_start_date=datetime(year=timezone.now().year, month=1, day=1).strftime("%Y-%m-%d"),
            application_end_date=datetime(year=timezone.now().year, month=12, day=31).strftime("%Y-%m-%d")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_res_admin_group(self.request.user)
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        super().form_valid(form)

        # attach all possible outcomes
        for o in models.Outcome.objects.all():
            models.ApplicationOutcome.objects.create(application=obj, outcome=o)

        # range = form.cleaned_data["date_range"]
        # if range:
        #     range = range.split("to")
        #     start_date = datetime.strptime(range[0].strip(), "%Y-%m-%d")
        #     obj.application_start_date = start_date
        #     if len(range) > 1:
        #         end_date = datetime.strptime(range[1].strip(), "%Y-%m-%d")
        #         obj.application_end_date = end_date
        #     else:
        #         obj.application_end_date = start_date
        return super().form_valid(form)


#
# class ApplicationUpdateView(CanModifyApplicationRequiredMixin, CommonUpdateView):
#     model = models.Application
#     form_class = forms.ApplicationForm
#     template_name = 'res/form.html'
#     home_url_name = "res:index"
#     grandparent_crumb = {"title": gettext_lazy("Applications"), "url": reverse_lazy("res:application_list")}
#     h2 = gettext_lazy("All fields are mandatory before approvals and submission")
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["is_admin"] = in_res_admin_group(self.request.user)
#         return context
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object(), "url": reverse_lazy("res:request_detail", args=[self.get_object().id])}
#
#     def form_valid(self, form):
#         obj = form.save(commit=False)
#         obj.updated_by = self.request.user
#         return super().form_valid(form)


class ApplicationDeleteView(CanModifyApplicationRequiredMixin, CommonDeleteView):
    model = models.Application
    success_url = reverse_lazy('res:application_list')
    template_name = 'res/confirm_delete.html'
    delete_protection = False
    grandparent_crumb = {"title": gettext_lazy("Applications"), "url": reverse_lazy("res:application_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("res:application_detail", args=[self.get_object().id])}


class ApplicationSubmitView(CanModifyApplicationRequiredMixin, CommonUpdateView):
    model = models.Application
    home_url_name = "res:index"
    template_name = 'res/application_submit.html'
    form_class = forms.ApplicationTimestampUpdateForm
    submit_text = gettext_lazy("Proceed")
    grandparent_crumb = {"title": gettext_lazy("Applications"), "url": reverse_lazy("res:application_list")}
    h2 = None


    def get_h1(self):
        my_object = self.get_object()
        if my_object.submission_date:
            return _("Do you wish to un-submit the following application?")
        else:
            return _("Do you wish to submit the following application to your accountable manager for their assessment and recommendation?")

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("res:application_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        if obj.submission_date:
            obj.submission_date = None
            if hasattr(obj, "recommendation"):
                recommendation = obj.recommendation
                recommendation.manager_signed = None
                recommendation.applicant_signed = None
                recommendation.save()
        else:
            obj.submission_date = timezone.now()
        obj.save()

        # if the request was just submitted, send an email
        if obj.submission_date:
            # create a recommendation
            try:
                recommendation, created = models.Recommendation.objects.get_or_create(application=obj, user=obj.manager)
            except IntegrityError:
                # means that there was a change in manager. Need to delete old recommendation and create new one
                get_object_or_404(models.Recommendation, application=obj).delete()
                recommendation, created = models.Recommendation.objects.get_or_create(application=obj, user=obj.manager)
            email = emails.NewRecommendationEmail(self.request, recommendation)
            email.send()

        return HttpResponseRedirect(self.get_success_url())


# class ApplicationCloneUpdateView(ApplicationUpdateView):
#     h1 = gettext_lazy("Clone an Application")
#     h2 = gettext_lazy("Please update the request details")
#
#     def test_func(self):
#         if self.request.user.id:
#             return True
#
#     def get_initial(self):
#         my_object = models.Application.objects.get(pk=self.kwargs["pk"])
#         data = dict(
#             title=f"COPY OF: {my_object.title}",
#             client=self.request.user,
#             advice_needed_by=None,
#         )
#         return data
#
#     def form_valid(self, form):
#         new_obj = form.save(commit=False)
#         new_obj.pk = None
#         new_obj.status = 1
#         new_obj.submission_date = None
#         new_obj.old_id = None
#         new_obj.uuid = None
#         new_obj.ref_number = None
#         new_obj.created_by = self.request.user
#         new_obj.save()
#         return HttpResponseRedirect(reverse_lazy("res:request_detail", args=[new_obj.id]))
