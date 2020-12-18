from scuba.mixins import LoginAccessRequiredMixin
from shared_models.views import CommonTemplateView


class IndexTemplateView(LoginAccessRequiredMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'scuba/index.html'
