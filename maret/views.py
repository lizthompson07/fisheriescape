from shared_models.views import CommonTemplateView

from maret.utils import UserRequiredMixin


# Create your views here.
class IndexView(UserRequiredMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'maret/index.html'
