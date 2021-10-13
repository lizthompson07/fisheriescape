from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy, gettext as _

from lib.functions.custom_functions import listrify
from res.mixins import LoginAccessRequiredMixin, ResAdminRequiredMixin, CanModifyApplicationRequiredMixin
from shared_models.views import CommonTemplateView, CommonFormsetView, CommonHardDeleteView, CommonCreateView, CommonFilterView, CommonDetailView, \
    CommonUpdateView, CommonDeleteView
from . import models, forms, filters, utils
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
    open_row_in_new_tab = True

    field_list = [
        {"name": 'id', "class": "", "width": "50px"},
        {"name": 'fiscal_year', "class": "", "width": "100px"},
        {"name": 'title|{}'.format(gettext_lazy("title")), "class": "w-35"},
        {"name": 'status', "class": "", "width": "100px"},
        {"name": 'has_process|{}'.format(gettext_lazy("has process?")), "class": "text-center", "width": "120px"},
        {"name": 'coordinator', "class": "", "width": "150px"},
        {"name": 'client', "class": "", "width": "150px"},
        {"name": 'region|{}'.format(gettext_lazy("region")), "class": "", "width": "75px"},
        {"name": 'sector|{}'.format(gettext_lazy("sector")), "class": ""},
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
        qp = self.request.GET
        qs = models.Application.objects.all()
        if qp.get("personalized"):
            qs = utils.get_related_applications(self.request.user)
        # qs = qs.annotate(search_term=Concat('title', Value(" "), 'translated_title', Value(" "), 'ref_number', output_field=TextField()))
        return qs

    def get_h1(self):
        qp = self.request.GET
        if qp.get("personalized"):
            return _("My Applications")
        return _("Applications")


class ApplicationDetailView(LoginAccessRequiredMixin, CommonDetailView):
    model = models.Application
    template_name = 'res/request_detail/main.html'
    home_url_name = "res:index"
    parent_crumb = {"title": gettext_lazy("Applications"), "url": reverse_lazy("res:application_list")}

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
            client=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_res_admin_group(self.request.user)
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super().form_valid(form)


class ApplicationUpdateView(CanModifyApplicationRequiredMixin, CommonUpdateView):
    model = models.Application
    form_class = forms.ApplicationForm
    template_name = 'res/form.html'
    home_url_name = "res:index"
    grandparent_crumb = {"title": gettext_lazy("Applications"), "url": reverse_lazy("res:application_list")}
    h2 = gettext_lazy("All fields are mandatory before approvals and submission")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_res_admin_group(self.request.user)
        return context

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("res:request_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class ApplicationDeleteView(CanModifyApplicationRequiredMixin, CommonDeleteView):
    model = models.Application
    success_url = reverse_lazy('res:application_list')
    template_name = 'res/confirm_delete.html'
    delete_protection = False
    grandparent_crumb = {"title": gettext_lazy("Applications"), "url": reverse_lazy("res:application_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("res:request_detail", args=[self.get_object().id])}


# class ApplicationSubmitView(ApplicationUpdateView):
#     template_name = 'res/request_submit.html'
#     form_class = forms.TripRequestTimestampUpdateForm
#     submit_text = gettext_lazy("Proceed")
#     h2 = None
#
#     def get_h1(self):
#         my_object = self.get_object()
#         if my_object.submission_date:
#             return _("Do you wish to un-submit the following request?")
#         else:
#             return _("Do you wish to submit the following request?")
#
#     def get_parent_crumb(self):
#         return {"title": truncate(self.get_object().title, 50), "url": reverse_lazy("res:request_detail", args=[self.get_object().id])}
#
#     def form_valid(self, form):
#         obj = form.save(commit=False)
#         obj.updated_by = self.request.user
#         if obj.submission_date:
#             obj.submission_date = None
#         else:
#             obj.submission_date = timezone.now()
#         obj.save()
#
#         # if the request was just submitted, send an email
#         if obj.submission_date:
#             email = emails.NewRequestEmail(self.request, obj)
#             email.send()
#         return HttpResponseRedirect(self.get_success_url())


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
