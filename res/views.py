from django.urls import reverse_lazy

from res.mixins import LoginAccessRequiredMixin, ResAdminRequiredMixin
from shared_models.views import CommonTemplateView, CommonFormsetView, CommonHardDeleteView
from . import models, forms, utils


class IndexTemplateView(LoginAccessRequiredMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'res/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = utils.in_res_admin_group(self.request.user)
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

