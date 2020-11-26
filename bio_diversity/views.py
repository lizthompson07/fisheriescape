from django.views.generic import TemplateView
from shared_models.views import CommonAuthCreateView
from django.urls import reverse_lazy

from . import models, forms


class IndexTemplateView(TemplateView):
    nav_menu = 'bio_diversity/bio_diversity_nav_menu.html'
    site_css = 'bio_diversity/bio_diversity_css.css'
    home_url_name = "bio_diversity:index"

    template_name = 'bio_diversity/index.html'


# CommonCreate Extends the UserPassesTestMixin used to determine if a user has
# has the correct privileges to interact with Creation Views
class CommonCreate(CommonAuthCreateView):

    nav_menu = 'bio_diversity/bio_diversity_nav.html'
    site_css = 'bio_diversity/bio_diversity.css'
    home_url_name = "bio_diversity:index"

    def get_success_url(self):
        return reverse_lazy("shared_models:close_me_no_refresh")

    # overrides the UserPassesTestMixin test to check that a user belongs to the whalesdb_admin group
    def test_func(self):
        return self.request.user.groups.filter(name='bio_diversity_admin').exists()


class InstCreate(CommonCreate):
    form_class = forms.InstForm
    model = models.InstDetCode
    title = "Some title"
