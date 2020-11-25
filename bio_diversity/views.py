from django.shortcuts import render
from django.views.generic import TemplateView
from shared_models.views import CommonCreateView

from . import models, forms
# Create your views here.


class IndexTemplateView(TemplateView):
    nav_menu = 'bio_diversity/bio_diversity_nav_menu.html'
    site_css = 'bio_diversity/bio_diversity_css.css'
    home_url_name = "bio_diversity:index"

    template_name = 'bio_diversity/index.html'


# CommonCreate Extends the UserPassesTestMixin used to determine if a user has
# has the correct privileges to interact with Creation Views
class CommonCreate(CommonCreateView):
    nav_menu = 'bio_diversity/bio_diversity_nav.html'
    site_css = 'bio_diversity/bio_diversity.css'
    home_url_name = "bio_diversity:index"


class CreateInst(CommonCreate):
    form_class = forms.InstForm
    model = models.InstDetCode
    title = "Some title"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)